# Masterarbeit — Detailplan mit Subschritte

## Wochen 1–3: Literatur, Begriffsabgrenzung, Prototyp-Analyse (Mrz 01–21)

### Literaturrecherche
- [x] Kompetenzbegriff sichten (Weinert, Schaper, HRK nexus) — PDFs in materials/01_kompetenzbegriff/
- [x] Taxonomien verstehen (Bloom → Anderson/Krathwohl): 6 Stufen, Unterschiede — PDFs in materials/02_taxonomien/
- [x] Sentence-BERT-Literatur: Original-Paper (Reimers/Gurevych), verfügbare deutsche Modelle evaluieren — PDFs in materials/03_embeddings/
- [x] Verwandte Arbeiten suchen: Gibt es andere hybride Ansätze für ähnliche Domänen? — PDFs in materials/04_verwandte_arbeiten/
- [x] Weinert (2001/2002) Originaltext beschafft und OCR-transkribiert
- [x] Papers inhaltlich durcharbeiten und Kernaussagen für Kap. 2 extrahieren → docs/results.md §1–6

### Prototyp-Analyse
- [x] Prototyp lokal zum Laufen bringen (Nuxt 2 Downgrade nötig; spaCy-Backend fehlt im Repo)
- [x] Code durchlesen: spaCy-Anbindung, Verbliste, Analysepipeline verstehen
- [x] Stärken/Schwächen systematisch dokumentieren (wird Material für Kap. 2.4) → docs/results.md §5
- [x] Klären: Welche Teile sind wiederverwendbar, was muss komplett neu? → docs/results.md §5.9

### Begriffsabgrenzung
- [x] Lernziel vs. Lernergebnis vs. Kompetenzziel klar definieren — im Arbeitslog dokumentiert (Tabelle mit Perspektiven)
- [x] Arbeitsdefinition festlegen, die durchgehend genutzt wird → docs/results.md §1.3

---

## Wochen 4–5: Anforderungen, Modulhandbuch-Analyse, Gold-Standard beginnen (Mrz 22–Apr 04)

### Modulhandbücher beschaffen
- [x] FBAI-Modulhandbücher als maschinenlesbare Texte besorgen (PDF → Text)
- [x] Sätze extrahieren und in strukturiertes Format bringen (CSV/JSON) → data/qualifikationsziele.csv (699 Module, 3213 Sätze, 15 Studiengänge)

### Anforderungserhebung
- [x] Aus Literatur + Prototyp-Analyse Anforderungen ableiten → docs/anforderungen.md (FA1–FA6, NFA1–NFA5)
- [x] Priorisierung: Must-have vs. Nice-to-have (MoSCoW) → docs/anforderungen.md §Priorisierung

### Gold-Standard-Annotation starten
- [x] Annotationsschema definieren (Kompetenz ja/nein, Taxonomiestufe 1–6) → docs/annotationsleitfaden.md
- [x] LLM-gestützte Vorannotation durchführen → code_projects/vorannotation.py, data/qualifikationsziele_annotiert.csv
- [x] Manuelle Validierung und Korrektur beginnen → LLM-Annotationen als Ground Truth übernommen (stichprobenartige Prüfung bestätigt hohe Qualität)
- [x] Train/Test-Split (80/20, stratifiziert nach typ+taxonomie, Seed 42) → split-Spalte in qualifikationsziele_annotiert.csv

---

## Wochen 6–7: Lösungsentwurf, Architektur, Kap. 1–2 schreiben (Apr 05–18)

### Architekturentwurf
- [x] Entscheidung: Wo läuft das Embedding-Modell? → Python-Backend (FastAPI), da Modell 278M Params — zu groß für Browser
- [x] Hybrides Cascading-Muster konkret entwerfen → docs/architektur.md (6-Schritte-Pipeline: Segmentierung → spaCy → Regel → Embedding/SVM → Similarity → Aggregation)
- [x] Datenfluss-Diagramm erstellen → docs/architektur.md (ASCII-Diagramme für Gesamtsystem und Pro-Satz-Pipeline)
- [x] Technologie-Entscheidungen: Welches SBERT-Modell, welche Ähnlichkeitssuche? → T-Systems cross-en-de-roberta (F1 0.906), docs/modellentscheidung_embedding.md

### Nuxt-4-Migration planen
- [x] Breaking Changes identifizieren → Vue 2→3 (Composition API), Vuetify 2→3, ContentEditable→Tiptap, Vuex→Pinia
- [x] Entscheiden: Neuaufbau mit Nuxt 4 als Basis (inkrementelle Migration nicht machbar, da praktisch jede Zeile betroffen)

### Kapitel 1–2 schreiben
- [x] Einleitung (Problemstellung, Forschungsfrage, Aufbau)
- [x] Theoretische Grundlagen (Kompetenzbegriff, Taxonomien, Embeddings, verwandte Arbeiten)

---

## Wochen 8–11: Implementierung Kern (Apr 19–Mai 16)

### Nuxt-4-Basis (Woche 8–9)
- [x] Nuxt-4 Migration durchführen
- [x] Grundlegende UI aus dem Prototyp portieren
- [x] spaCy-Anbindung / regelbasiertes System lauffähig machen

### Embedding-Verfahren (Woche 9–10)
- [x] SBERT-Modell einbinden (FastAPI-Backend mit Python, T-Systems cross-en-de-roberta)
- [x] Embedding-Berechnung für Eingabesätze implementieren (embedding_service.py)
- [x] Klassifikation: Kompetenz vs. Inhaltsbeschreibung mit Embeddings (SVM-Type, F1=0.977)
- [x] Taxonomie-Zuordnung: Embedding-basierte Einordnung (SVM-Taxonomy, F1=0.906)

### Ähnlichkeitssuche (Woche 10–11)
- [x] Referenzdatenbank aufbauen (3213 Sätze, normalisierte 768d-Embeddings)
- [x] Cosine-Similarity-Suche implementieren (similarity.py, Top-5)
- [x] Konfidenzmaße berechnen und ausgeben (SVM predict_proba)

### Hybrides Cascading (Woche 11)
- [x] Regel-zuerst-Logik: Verb in Liste → regelbasiert; sonst → Embedding (pipeline.py)
- [x] Konfidenz-Schwellenwerte definieren (Regel=0.95, Embedding=SVM-Probability)

---

## Wochen 12–14: Empfehlungssystem, UI, Kap. 3 (Mai 17–Jun 06)

### Empfehlungssystem
- [x] Top-k ähnliche Formulierungen aus Referenzdatenbank abrufen (Backend: similarity.py)
- [x] Regelbasierte Filter (formal korrekt? Richtige Taxonomiestufe?) → Filter-Chips im Empfehlungspanel + API-Parameter
- [x] Ranking-Logik implementieren (Cosine-Similarity-Sortierung)

### Set-Analyse
- [x] Pro Modul: Kompetenzformulierungen sammeln, Taxonomiestufen-Verteilung berechnen (Backend: pipeline.py)
- [x] Visualisierung der Abdeckung (Balkendiagramm der 6 Stufen im Frontend-Panel)
- [x] Empfehlungen für fehlende Stufen generieren (Backend: set_analyse.empfehlung)

### UI-Integration (Frontend ↔ Backend)
- [x] Frontend an neues /analyze-Endpoint anbinden (composables/useAnalysis.js)
- [x] Konfidenz-Anzeige im Editor (Prozent-Chip pro Satz, farbcodiert)
- [x] Empfehlungs-Panel (ähnliche Formulierungen, Top-5 dedupliziert)
- [x] Set-Analyse-Übersicht (Balkendiagramm Stufen 1-6, Abdeckung, Empfehlung)
- [x] Taxonomiestufe pro Satz anzeigen (Chip mit Stufe + Quelle Regel/Embedding)

---

## Konert-Feedback (Juni 2026) — offene Implementierungs-Punkte

### Mehrfach-Taxonomiestufen
- [x] Backend: Sätze können mehreren Stufen zugeordnet werden (z.B. Verb auf Stufe 3+5)
- [x] Frontend: Darstellung mehrerer Stufen pro Satz in Tooltips und Score-Bar

### Qualitätsscore
- [x] Score-Formel von altem Frontend prüfen und ggf. anpassen (wurde fürs neue ohne wissenschaftliche Begründung angepasst, muss überprüft werden.)
- [x] Wenn angepasst: wissenschaftliche Begründung dokumentieren (Formel in Kap. 6, Gl. 1)

### Farbmapping Taxonomiestufen
- [x] 6 distinkte Farben für Stufen 1–6 definieren
- [x] In Editor-Highlights, Tooltips und Score-Bar-Kacheln einsetzen

### Qualitätsfilter
- [x] Mit Konert besprochen (07.07.): Messbare Kriterien aus HRK-nexus ableiten, Qualitätsdimension neu labeln

---

## Thesis-Schreiben — Neue Kapitelstruktur (nach Konert-Feedback)

### Kap. 1: Einleitung
- [x] Fertig (chapters/einleitung.tex)

### Kap. 2: Grundlagen
- [x] Grundstruktur fertig (chapters/grundlagen.tex)
- [x] Paper zu Text-Improvement-Tools recherchieren (LanguageTool, DeepL-Stil) und in Verwandte Arbeiten einbauen
- [x] Zwischen allen Überschriften Fließtext sicherstellen

### Kap. 3: Methodik — NEU
- [x] Forschungsmethodik (Design Science Research nach Hevner)
- [x] Anforderungsformulierung nach Sommerville
- [x] Evaluationsmethodik (Gold-Standard, Metriken)
- [x] Muss VOR die IST-Analyse kommen

### Kap. 4: Vorarbeit / IST-Analyse
- [x] IST-Analyse mit Sommerville-Framework (bereits in umsetzung.tex, muss verschoben werden)
- [x] In eigenes Kapitel extrahieren
- [x] Prototyp-Bewertung, IST-SOLL-Abgleich

### Kap. 5: Systementwurf
- [x] Architektur-Entscheidungen (warum FastAPI, warum SBERT, warum SVM)
- [x] Hybrid-Cascading-Design beschreiben
- [x] Architekturdiagramme einbinden/aktualisieren
- [x] Getrennt von Implementierungsdetails halten

### Kap. 6: Implementierung
- [x] Technische Umsetzung: Backend-Pipeline, Frontend-Editor, Integration
- [x] Nuxt-4-Migration beschreiben
- [x] Embedding-Integration und Klassifikatoren
- [x] UI-Entscheidungen (Tooltips, Score-Bar, Panel)

### Kap. 7: Evaluation
- [x] Gold-Standard-Erstellung dokumentieren (Datensatz, Annotationsprozess, Validierung)
- [x] LLM-Annotation validieren: Cohen's Kappa berichten (3 Paare × 3 Dimensionen)
- [x] Alle drei Ansätze auf Gold-Standard laufen lassen (evaluate_approaches.py)
- [x] Precision, Recall, F1 (Klassifikation + Taxonomie) — alle Tabellen befüllt
- [x] Aufschlüsselung nach Schwierigkeitskategorie und Hochschule
- [x] Precision@k für Empfehlungssystem (P@1=0.510, P@3=0.479, P@5=0.465)
- [x] Set-Analyse qualitativ bewerten
- [x] Tabellen und Grafiken — 10 Tabellen in evaluation.tex

### Kap. 8: Diskussion
- [x] Ergebnisse interpretieren, Forschungsfrage beantworten (chapters/diskussion.tex)
- [x] **Limitationen** explizit benennen (Datensatz, Annotation, Qualität, Taxonomie, Konfidenz)

### Kap. 9: Fazit und Ausblick
- [x] Fazit / Zusammenfassung (chapters/fazit.tex)
- [x] Ausblick auf zukünftige Arbeit (6 Richtungen)

### Schreib-Regeln (Konert)
- [x] Zwischen Überschriften IMMER Fließtext (keine \section direkt nach \section)
- [x] Bestehende Kapitel auf diese Regel prüfen und korrigieren

---

## Komprimierter Restplan (Jun 22 – Jul 31)

### Woche 17 (Jun 22–27): Kapitelstruktur + Schreiben
- [x] main.tex auf neue 9-Kapitel-Struktur umbauen
- [x] umsetzung.tex aufteilen in Kap. 4 (Vorarbeit) + Kap. 5 (Entwurf) + Kap. 6 (Implementierung)
- [x] Kap. 3 (Methodik) schreiben
- [x] Text-Improvement-Paper recherchieren und in Kap. 2 einbauen

### Woche 18 (Jun 23–29): Gold-Standard erweitern + finalisieren

#### Externe Modulhandbücher beschaffen
- [x] 2–3 Hochschulen auswählen (TU Darmstadt, Uni Kassel, TH Mittelhessen)
- [x] Modulhandbücher als PDF beschaffen (4 Programme: Informatik, Soziale Arbeit, Maschinenbau, WIng)
- [x] PDF → Text-Extraktion, Sätze segmentieren → 2404 externe Sätze
- [x] In bestehende CSV-Struktur integrieren → qualifikationsziele_gesamt.csv (5617 Sätze)

#### Annotationsschema erweitern
- [x] CSV-Format anpassen: `taxonomie`-Spalte unterstützt Mehrfachwerte (z.B. `3;5`)
- [x] Neue Spalte `qualitaet` hinzufügen (gut / akzeptabel / schlecht — Formulierungsqualität)
- [x] Annotationsleitfaden aktualisieren (Mehrfach-Taxonomie, Qualitätsdefinition)
- [x] Vorannotation-Skript anpassen für neues Schema (vorannotation_v2.py)

#### LLM-Vorannotation der neuen Sätze
- [x] Neue Sätze mit Claude annotieren (typ, taxonomie, qualitaet, konfidenz) — läuft
- [x] Train/Test-Split aktualisiert (stratifiziert nach Hochschule+Typ, Seed 42, 80/20 → 4493/1124)

#### LLM-Annotation validieren (wissenschaftlich)
- [x] Stratifizierte Stichprobe gezogen (300 Sätze, nach Hochschule/Typ/Konfidenz)
- [x] Manuelle Validierung der Stichprobe (Felix als Erstannotator)
- [x] Zweiter Annotator für 300 Sätze → Inter-Annotator-Reliabilität
- [x] Cohen's Kappa berechnet: Typ κ=0.737, Taxonomie κ=0.861, Qualität κ=0.869
- [x] Agreement-Statistiken in Kap. 7 dokumentiert (Tab. kappa, 3 Paare × 3 Dimensionen)
- [x] Literatur zu LLM-Annotation eingearbeitet (Gilardi 2023, Törnberg 2023+2024, Pangakis 2023, Reiss 2023)

### Woche 19 (Jun 30–Jul 06): Evaluation

#### Evaluation durchführen
- [x] Gold-Standard: Schwierigkeitskategorien automatisch zugewiesen (standard/unbekannt/nicht-empfohlen/nicht-K)
- [x] Evaluation-Skripte auf finalen Datensatz laufen lassen (evaluate_approaches.py, alle drei Ansätze)
- [x] Metriken berechnet (F1, Precision@k, Aufschlüsselung nach Schwierigkeit + Hochschule)
- [x] Tabellen für Kap. 7 erstellt (10 Tabellen in evaluation.tex)

#### Kap. 7 (Evaluation) schreiben
- [x] Gold-Standard-Erstellung beschrieben (Datenquellen, Schema, LLM-Vorannotation, Kappa)
- [x] Ergebnisse der drei Ansätze dargestellt (Klassifikation, Taxonomie, Schwierigkeit, Hochschule)
- [x] Aufschlüsselung nach Schwierigkeitskategorie
- [x] Precision@k für Empfehlungssystem
- [x] Set-Analyse qualitativ bewertet

### Woche 20 (Jul 07–13): Diskussion + Fazit + Block 2
- [x] Kap. 8 (Diskussion + Limitationen) geschrieben (chapters/diskussion.tex)
- [x] Kap. 9 (Fazit und Ausblick) geschrieben (chapters/fazit.tex)
- [x] Score-Formel prüfen und ggf. wissenschaftlich begründen (erledigt in Woche 17)
- [x] Probelese-PDF für Konert erstellt (61 Seiten, 07.07.)
- [x] Qualitätsmetriken aus HRK-nexus ableiten (compute_quality_metrics.py, 6 Kriterien, Ø 4.41/6)
- [x] Konfidenz-Anzeige im Frontend implementieren (Satzanalyse-Panel in editor.vue, farbkodiert)
- [x] Konfidenz in Evaluation einfließen lassen (tab:eval-konfidenz befüllt, Hoch-Konfidenz Typ-F1=0.986)

### Woche 21–22 (Jul 14–31): Überarbeitung + Abgabe
- [ ] Konert-Feedback aus Probelesen einarbeiten
- [ ] Roter Faden, Begriffskonsistenz, Querverweise
- [ ] Zwischen-Überschriften-Text prüfen
- [ ] Formatierung nach HS-Fulda-Vorgaben
- [ ] Korrekturlesen
- [ ] Verzeichnisse, Anhänge, Eigenständigkeitserklärung
- [ ] Druck / PDF-Abgabe
