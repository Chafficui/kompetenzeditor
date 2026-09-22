# Kompetenzeditor — Hybride NLP-Pipeline für Kompetenzformulierungen

Repository zur Masterarbeit von Felix Beinßen, Hochschule Fulda (Betreuer: Prof. Johannes Konert).

Die Arbeit untersucht Qualifikationsziele in Modulhandbüchern deutscher Hochschulen mit
einer hybriden NLP-Pipeline (regelbasiert + Sentence-Embeddings) und stellt die Ergebnisse
über ein Editor-Werkzeug bereit, den **Kompetenzeditor**. Die Pipeline übernimmt drei Aufgaben:

- **Satztyp-Klassifikation**: Kompetenzformulierung (K), Inhaltsbeschreibung (I) oder
  Sonstiges (S)
- **Taxonomiestufe** 1–6 nach Anderson & Krathwohl (Erinnern, Verstehen, Anwenden,
  Analysieren, Bewerten, Erschaffen) für K-Sätze
- **Qualitätsbewertung** (gut / akzeptabel / schlecht) und **Ähnlichkeitssuche** für
  Formulierungsvorschläge

## Struktur

```
Masterarbeit/
├── code_projects/
│   ├── backend/                  FastAPI-Backend der Analyse-Pipeline
│   ├── kompetenzeditor/          Nuxt-4-Frontend (Editor-Werkzeug)
│   ├── lot_kohnert_prototype/    Vorgänger-Prototyp (Referenz, siehe unten)
│   └── *.py                      Skripte der Datenpipeline & Evaluation
├── data/                         CSV-Datensätze (Gold-Standard, Annotationen, Stichproben)
├── evaluation_results/           Auswertungen des Ansatzvergleichs
└── materials/                    Quell-PDFs der Modulhandbücher (nicht im Repo, siehe materials/README.md)
```

Details zu den einzelnen Bereichen stehen in den jeweiligen README-Dateien:
[`data/README.md`](data/README.md), [`materials/README.md`](materials/README.md),
[`code_projects/kompetenzeditor/README.md`](code_projects/kompetenzeditor/README.md).

## Das Werkzeug: Kompetenzeditor

Ein Nuxt-4-Frontend (Vuetify, TipTap-Editor, Pinia, Dexie/IndexedDB für lokale
Speicherung im Browser) kommuniziert mit einem FastAPI-Backend, das die Analyse-Pipeline
ausführt. Der Editor markiert Verben im Text, zeigt Taxonomiestufen und Qualitätshinweise
an und schlägt ähnliche, gut bewertete Formulierungen aus dem Gold-Standard vor.

## Schnellstart

### Backend (FastAPI, Python 3.11)

```bash
cd code_projects/backend
pip install -r requirements.txt
python -m spacy download de_core_news_lg

# Modelle erzeugen (werden nicht mitversioniert, liegen in backend/models/)
python train_classifiers.py      # SVM-Klassifikatoren für Typ & Taxonomie (joblib)
python build_reference_db.py     # Referenz-Embeddings + Metadaten für die Ähnlichkeitssuche

uvicorn main:app --host 0.0.0.0 --port 8000
```

Beide Skripte greifen auf `data/goldstandard.csv` zu und müssen einmalig ausgeführt werden,
bevor das Backend vollständig funktioniert (`train_classifiers.py` benötigt außerdem den
Split `train`/`test`). Das Backend lädt beim Start zusätzlich das SBERT-Modell
`T-Systems-onsite/cross-en-de-roberta-sentence-transformer` und das spaCy-Modell
`de_core_news_lg`. Endpunkte: `GET /health`, `POST /analyze {text}` (Port 8000).

Alternativ per Docker (baut nur das Backend, Modelle/Daten werden aus dem Host gemountet):

```bash
cd code_projects/kompetenzeditor
docker compose up --build
```

### Frontend (Nuxt 4, bun)

```bash
cd code_projects/kompetenzeditor
bun install       # alternativ: npm install
bun run dev        # alternativ: npm run dev
```

Der Dev-Server proxyt `/api`-Anfragen an `http://127.0.0.1:8000` (das Backend muss also
parallel laufen). Details zum Frontend in [`code_projects/kompetenzeditor/README.md`](code_projects/kompetenzeditor/README.md).

## Datensatz

Der Gold-Standard-Datensatz (`data/goldstandard.csv`) umfasst **5.617 annotierte Sätze**
aus **866 Modul-/Studiengang-Kombinationen** in **18 Studiengängen** an **4 Hochschulen**:

| Hochschule | Sätze |
|---|---:|
| Hochschule Fulda | 3.213 |
| TH Mittelhessen | 1.468 |
| TU Darmstadt | 896 |
| Universität Kassel | 40 |

Satztyp: 5.174 K (Kompetenzformulierung), 188 I (Inhaltsbeschreibung), 255 S (Sonstiges).
Qualität: 1.980 gut, 2.938 akzeptabel, 699 schlecht. Train/Test-Split: 4.493 / 1.124 Sätze
(stratifiziert nach Hochschule und Typ).

Die Entstehung des Datensatzes (PDF-Extraktion → LLM-Vorannotation → manuelle
Gold-Standard-Annotation → Validierung) sowie alle CSV-Dateien sind in
[`data/README.md`](data/README.md) beschrieben.

## Reproduktion der Evaluation

Die Skripte in `code_projects/` bilden die Datenpipeline in dieser Reihenfolge ab
(Details und Aufrufparameter in `data/README.md`):

1. `extract_qualifikationsziele.py`, `extract_externe_modulhandbuecher.py` — Extraktion aus den Quell-PDFs in `materials/`
2. `vorannotation.py` / `vorannotation_v2.py` — LLM-gestützte Vorannotation (Anthropic API, `ANTHROPIC_API_KEY` erforderlich, Default-Modell `claude-sonnet-4-6`)
3. `sample_goldstandard.py`, `annotation_tool.py` — Stichprobenziehung und manuelle Gold-Standard-Annotation
4. `add_quality_heuristic.py`, `compute_quality_metrics.py` — Qualitätsbewertung
5. `merge_goldstandard.py` — Zusammenführung zu `data/goldstandard.csv` inkl. Train/Test-Split
6. `sample_validation.py` — Ziehung der Validierungsstichprobe (300 Sätze, zwei Annotatoren)

Der Ansatzvergleich (regelbasiert vs. Embedding vs. hybrid) wird reproduziert mit:

```bash
cd code_projects
python evaluate_approaches.py
```

Das Skript benötigt die trainierten Modelle in `code_projects/backend/models/`
(siehe Schnellstart) und schreibt die Ergebnisse nach `evaluation_results/`.
Ergänzende Auswertungen: `evaluate_embeddings.py` (Modellvergleich), `evaluate_confidence*.py`
(Konfidenz-Bins), `evaluate_correlation.py`, `evaluate_pk_clean.py` (Precision@k ohne
Test-Set-Leakage).

### Kernergebnisse (aus `evaluation_results/evaluation_report.txt`)

Gewichtetes F1 auf dem Test-Split (1.124 Sätze):

| Ansatz | Typ-F1 (K/I/S) | Taxonomie-F1 (1–6) |
|---|---:|---:|
| Regelbasiert | 0,819 | 0,581 |
| Embedding (SBERT + SVM) | **0,963** | **0,839** |
| Hybrid (Regel + Embedding) | 0,929 | 0,713 |

Alle paarweisen Unterschiede sind laut McNemar-Test (Bonferroni-korrigiert,
α = 0,05/6 ≈ 0,0083) signifikant. Details, Konfusionsmatrizen und Aufschlüsselungen
nach Hochschule/Schwierigkeitskategorie stehen in `evaluation_results/evaluation_report.txt`.

## Verwandte Arbeit

Der Ordner `code_projects/lot_kohnert_prototype/` enthält als Referenz den
Vorgänger-Prototyp „Kompetenzeditor“ von Ludwig Loth
(Ursprung: <https://github.com/ludwig-loth/kompetenzeditor>, MIT-Lizenz, eigene
`LICENSE.txt`). Er ist nicht Teil des in dieser Arbeit entwickelten Tools, sondern
diente als konzeptioneller Ausgangspunkt.

> Loth, L.; Konert, J. (2022): Erstellung eines NLP-basierten Editors mit
> Qualitätsindikatoren und Änderungsvorschlägen für Kompetenzbeschreibungen.
> DELFI Workshops 2022. DOI: [10.18420/delfi2022-ws-32](https://doi.org/10.18420/delfi2022-ws-32)

## Lizenz

Der Code in diesem Repository steht unter der MIT-Lizenz (Copyright 2026 Felix Beinßen),
siehe `LICENSE`. Der Prototyp in `code_projects/lot_kohnert_prototype/` steht unter einer
eigenen MIT-Lizenz (Copyright Ludwig Loth), siehe dessen `LICENSE.txt`.

Die Annotationen und Auswertungen in `data/` und `evaluation_results/` stehen unter
CC BY 4.0. Die Satztexte selbst stammen aus öffentlich zugänglichen Modulhandbüchern der
genannten Hochschulen; das Urheberrecht an den Originaltexten liegt bei den jeweiligen
Hochschulen.

## Zitation

Ein Zitiervorschlag findet sich in `CITATION.cff`.
