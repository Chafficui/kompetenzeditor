# Daten

Dieser Ordner enthält den Gold-Standard-Datensatz sowie alle Zwischenstände, die bei
seiner Entstehung anfielen. Grundlage sind die Quell-PDFs in `materials/` (siehe
[`materials/README.md`](../materials/README.md)); die Erzeugung der Dateien ist in
den Skripten unter `code_projects/` implementiert.

## Entstehung (Pipeline-Reihenfolge)

1. **Extraktion** aus den Modulhandbuch-PDFs
   - `code_projects/extract_qualifikationsziele.py` — Hochschule Fulda (PyMuPDF) → `qualifikationsziele.csv`
   - `code_projects/extract_externe_modulhandbuecher.py` — externe Hochschulen (`pdftotext`/poppler) → `qualifikationsziele_extern.csv`
2. **LLM-gestützte Vorannotation** (Satztyp, Taxonomiestufe, ab v2 zusätzlich Qualität und
   Mehrfach-Taxonomie) über die Anthropic API
   - `code_projects/vorannotation.py` / `vorannotation_v2.py`
   - benötigt `ANTHROPIC_API_KEY`; Default-Modell laut Code: `claude-sonnet-4-6`
   - → `qualifikationsziele_annotiert.csv`, `qualifikationsziele_fulda_annotiert_v2.csv`, `qualifikationsziele_extern_annotiert.csv`
3. **Stichprobenziehung und manuelle Gold-Standard-Annotation**
   - `code_projects/sample_goldstandard.py` zieht eine geschichtete 300er-Stichprobe → `goldstandard_sample.csv`
   - `code_projects/annotation_tool.py` (lokales Web-Tool, Port 8888) für die manuelle Korrektur/Bestätigung
4. **Qualitätsbewertung**
   - `code_projects/add_quality_heuristic.py` ergänzt eine heuristische `qualitaet`-Spalte
   - `code_projects/compute_quality_metrics.py` berechnet Qualitätsindikatoren nach den HRK-nexus-Leitlinien
5. **Zusammenführung**
   - `code_projects/merge_goldstandard.py` führt die re-annotierten HS-Fulda-Daten (v2) und
     die externen Annotationen zusammen und erzeugt einen stratifizierten 80/20-Train/Test-Split
     (Schichtung nach Hochschule + Typ) → **`goldstandard.csv`**
6. **Validierung**
   - `code_projects/sample_validation.py` zieht eine stratifizierte 300er-Stichprobe aus dem
     Gold-Standard (Schichtung nach Hochschule, Taxonomiestufe, LLM-Konfidenz) → `validierungsstichprobe.csv`
   - zwei unabhängige Annotatoren prüfen die Stichprobe manuell → `validierung_annotiert_erstannotator.csv`,
     `validierung_annotiert_zweitannotator.csv`

`qualifikationsziele_gesamt.csv` ist ein Zwischenstand vor der Re-Annotation der
HS-Fulda-Daten und `qualifikationsziele_fulda_reannotation.csv` die dafür verwendete
(leere) Eingabevorlage.

## Dateien

| Datei | Inhalt | Zeilen (ohne Header) |
|---|---|---:|
| `goldstandard.csv` | **Finaler Gold-Standard-Datensatz** mit Train/Test-Split | 5.617 |
| `goldstandard_sample.csv` | 300er-Stichprobe für die manuelle Gold-Standard-Annotation (LLM-Vorschlag + manuelle Korrektur) | 300 |
| `qualifikationsziele.csv` | Rohextrakt der Qualifikationsziele, Hochschule Fulda (unannotiert) | 3.213 |
| `qualifikationsziele_annotiert.csv` | Fulda-Extrakt mit LLM-Vorannotation v1 (Typ, einfache Taxonomie, Konfidenz, Split) | 3.213 |
| `qualifikationsziele_extern.csv` | Rohextrakt der externen Modulhandbücher (THM, Uni Kassel, TU Darmstadt), unannotiert | 2.404 |
| `qualifikationsziele_extern_annotiert.csv` | Externe Sätze mit LLM-Vorannotation v2 (Typ, Taxonomie, Qualität, Konfidenz) | 2.404 |
| `qualifikationsziele_fulda_annotiert_v2.csv` | Fulda-Sätze, re-annotiert mit Schema v2 (Mehrfach-Taxonomie, Qualität); Grundlage für `goldstandard.csv` | 3.213 |
| `qualifikationsziele_fulda_reannotation.csv` | Leere Eingabevorlage für die Re-Annotation der Fulda-Sätze (Schema v2, alle Annotationsspalten leer) | 3.213 |
| `qualifikationsziele_gesamt.csv` | Zwischenstand (Fulda + extern) vor der Fulda-Re-Annotation | 5.617 |
| `validierungsstichprobe.csv` | Stratifizierte 300er-Validierungsstichprobe aus dem Gold-Standard, mit leeren `val_*`-Spalten | 300 |
| `validierung_annotieren.csv` | Vorlage für die Validierung (Kurzformat: nur `nr`, `hochschule`, `modulname`, `satz` + leere `val_*`-Spalten) | 300 |
| `validierung_annotiert_erstannotator.csv` | Validierungsstichprobe, ausgefüllt vom ersten Annotator | 300 |
| `validierung_annotiert_zweitannotator.csv` | Validierungsstichprobe, ausgefüllt vom zweiten Annotator | 300 |

## Spaltenbeschreibung

**`goldstandard.csv`**: `studiengang`, `hochschule`, `modul_id`, `modulname`, `satz_nr`,
`satz`, `typ` (K/I/S), `taxonomie` (1–6, bei Mehrfachzuordnung `;`-getrennt, z. B. `3;5`;
die Primärstufe ist der erste Wert), `qualitaet` (gut/akzeptabel/schlecht), `konfidenz`
(LLM-Konfidenz 0.0–1.0), `split` (train/test).

**`qualifikationsziele*.csv`** (Rohextrakte): `studiengang`, (`hochschule`, nur extern),
`modul_id`, `modulname`, `satz_nr`, `satz`.

**`*_annotiert*.csv`**: wie oben, zusätzlich `typ`, `taxonomie`, ggf. `qualitaet`,
`konfidenz`, ggf. `split`.

**`goldstandard_sample.csv`**: `studiengang`, `modul_id`, `modulname`, `satz_nr`, `satz`,
`llm_typ`, `llm_taxonomie`, `llm_konfidenz` (LLM-Vorschlag), `typ`, `taxonomie`
(manuelle Korrektur), `kommentar`.

**`validierung*.csv`**: `nr`, `hochschule`, `modulname`, `satz`, `val_typ`,
`val_taxonomie`, `val_qualitaet`, `val_kommentar` (jeweils manuelle Zweitmeinung);
`validierungsstichprobe.csv` enthält zusätzlich alle Gold-Standard-Spalten als Referenz.

## Statistik des Gold-Standards (`goldstandard.csv`)

- 5.617 Sätze, 866 Modul-/Studiengang-Kombinationen, 18 Studiengänge, 4 Hochschulen
- Hochschule: Hochschule Fulda 3.213, TH Mittelhessen 1.468, TU Darmstadt 896, Universität Kassel 40
- Typ: K 5.174, I 188, S 255
- Qualität: gut 1.980, akzeptabel 2.938, schlecht 699
- Split: train 4.493, test 1.124
- Primär-Taxonomiestufe (nur K-Sätze): 1 (Erinnern) 1.082, 2 (Verstehen) 1.203,
  3 (Anwenden) 1.890, 4 (Analysieren) 307, 5 (Bewerten) 458, 6 (Erschaffen) 234
- 1.770 Sätze tragen mehr als eine Taxonomiestufe (`;`-getrennt)

## Weiterverwendung

`code_projects/backend/train_classifiers.py` und `code_projects/backend/build_reference_db.py`
lesen `goldstandard.csv` direkt ein, um die SVM-Klassifikatoren bzw. die Referenz-Datenbank
für die Ähnlichkeitssuche des Backends zu erzeugen. `code_projects/evaluate_approaches.py`
wertet den Test-Split aus (siehe Root-`README.md`, Abschnitt „Reproduktion der Evaluation“).
