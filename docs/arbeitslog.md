# Arbeitslog Masterarbeit

Chronologische Dokumentation aller Arbeitsschritte. Dient als Rohmaterial für die Thesis.

---

## 2026-06-23

### Externe Modulhandbuecher fuer Gold-Standard-Datensatz recherchiert und heruntergeladen
- **Ziel**: 3 oeffentlich zugaengliche Modulhandbuecher (Informatik B.Sc.) von anderen deutschen Hochschulen als Datenquellen fuer die Evaluation identifizieren (TU, Uni, FH/HAW)
- **Gefundene Quellen**:
  1. **TU Darmstadt** — B.Sc. Informatik PO 2023 (610 S., 291 Module mit "Qualifikationsziele / Lernergebnisse")
  2. **Uni Kassel** — B.Sc. Informatik (91 S., 72 Module mit "Lernergebnisse, Kompetenzen, Qualifikationsziele")
  3. **Frankfurt UAS** — B.Sc. Informatik (110 S., 19 Module mit "Lernergebnisse und Kompetenzen")
  4. **TH Mittelhessen** — B.Sc. Informatik PO 2023 v5 (134 Module mit "Qualifikationsziele und angestrebte Lernergebnisse")
- **Ergebnis**: Alle 4 PDFs heruntergeladen nach `materials/modulhandbuecher_extern/`; alle enthalten strukturierte Kompetenzformulierungen auf Modulebene mit typischen Verben ("koennen", "sind in der Lage", "verfuegen ueber", "beherrschen"). TU Darmstadt und THM besonders reichhaltig. Beste 3 fuer Gold-Standard: TU Darmstadt (TU), Uni Kassel (Uni), Frankfurt UAS oder THM (FH/HAW).

### Nicht-Informatik Modulhandbuecher fuer Diversitaet im Gold-Standard heruntergeladen
- **Ziel**: 3-4 Modulhandbuecher aus anderen Fachbereichen (nicht Informatik) beschaffen, um den Gold-Standard-Datensatz fachlich zu diversifizieren
- **Gefundene Quellen**:
  1. **Uni Kassel — Soziale Arbeit B.A.** (36 S., Aenderungsordnung 21.06.2023)
  2. **THM — Maschinenbau B.Sc.** (162 S., Version 3 vom 24.03.2025)
  3. **THM — Wirtschaftsingenieurwesen B.Sc.** (202 S., Version 10 vom 03.06.2025)
  4. **TH Koeln — Soziale Arbeit B.A.** (44 S., Stand Oktober 2025, PO 4.0)
- **Ergebnis**: Alle PDFs nach `materials/modulhandbuecher_extern/` heruntergeladen.

### PDF-Extraktion externe Modulhandbuecher
- **Ziel**: Qualifikationsziele aus 4 externen PDFs extrahieren (TU Darmstadt, Uni Kassel, THM Maschinenbau, THM WIng)
- **Vorgehen**: `pdftotext` fuer Textextraktion (pdfplumber/pdfminer crashten bei grossen PDFs), dann regex-basiertes Parsing pro Hochschulformat
- **Ergebnis**: 2404 Sätze aus 3 Hochschulen / 4 Studiengängen extrahiert
  - TH Mittelhessen: 136 Module, 1468 Sätze (Maschinenbau + WIng)
  - TU Darmstadt: 41 Module, 896 Sätze (Informatik)
  - Universität Kassel: 17 Module, 40 Sätze (Soziale Arbeit)
- **Output**: `data/qualifikationsziele_extern.csv`, Skript: `code_projects/extract_externe_modulhandbuecher.py`

### Annotationsschema erweitert
- **Ziel**: Gold-Standard-Schema um Mehrfach-Taxonomie und Formulierungsqualitaet erweitern
- **Änderungen**:
  - `taxonomie`-Spalte unterstuetzt jetzt Mehrfachwerte (z.B. `3;5`)
  - Neue Spalte `qualitaet` (gut / akzeptabel / schlecht)
  - Neue Spalte `hochschule` (HS Fulda, TU Darmstadt, TH Mittelhessen, Uni Kassel)
- **Aktualisierte Dokumente**: `docs/annotationsleitfaden.md`, `code_projects/vorannotation_v2.py`

### LLM-Vorannotation gestartet (extern + HS Fulda Re-Annotation)
- **Ziel**: Alle 5617 Sätze mit Claude Sonnet im neuen Schema annotieren (typ, taxonomie mit Mehrfachwerten, qualitaet, konfidenz)
- **Extern**: 2404 Sätze fertig annotiert (88% K, 5% I, 7% S, 32.6% Mehrfach-Taxonomie)
- **HS Fulda**: 3213 Sätze Re-Annotation läuft (altes Schema hatte keine Mehrfach-Taxonomie und Qualität)
- **Output**: `data/qualifikationsziele_extern_annotiert.csv`, `data/qualifikationsziele_fulda_annotiert_v2.csv`

### Kap. 7 (Evaluation) als Gerüst geschrieben
- **Inhalt**: Vollständige Kapitelstruktur mit allen Subsections, Tabellen und \todo-Markern
- **Sections**: Gold-Standard (Datenquellen, Schema, Vorannotation, Kappa), Vergleichende Evaluation (Klassifikation, Taxonomie, Schwierigkeit, Hochschule), Empfehlungssystem, Set-Analyse
- **LLM-Literatur**: Vorannotations-Absatz mit Gilardi (2023), Törnberg (2025), Pangakis (2023), Reiss (2023), Törnberg (2024) eingebaut
- **BibTeX**: 7 neue Einträge (cohen1960coefficient, landis1977measurement, gilardi2023chatgpt, tornberg2025llm, tornberg2024bestpractices, pangakis2023validation, reiss2023testing)

### Konsistenz-Review und Fixes über alle Kapitel
- **Datensatz-Zahlen**: Kap. 1, 3, 5 von "3213 Sätze HS Fulda" auf "5600+ Sätze, 4 Hochschulen, 4 Fachbereiche" aktualisiert
- **Taxonomie-Terminologie**: "Evaluieren/Kreieren" durchgängig zu "Bewerten/Erschaffen" vereinheitlicht (Kap. 1, 2)
- **Vuetify-Version**: "Vuetify~3" → "Vuetify~4" korrigiert (Kap. 6)
- **Methodik (Kap. 3)**: Annotationsschema auf 3 Dimensionen aktualisiert (typ, taxonomie mit Mehrfachzuordnung, qualitaet)
- **Referenzdatenbank (Kap. 5)**: Auf erweiterten Datensatz aktualisiert, Modellauswahl als "initiale Evaluation" kontextualisiert
- **merge_goldstandard.py**: Auf neue v2-Dateien umgestellt

### Kappa-Neuberechnung nach erneuter Zweitannotation und Einpflegen in Kap. 7
- **Anlass**: Zweitannotation wurde wiederholt, da erste Runde unbefriedigend war
- **Ergebnis**: Deutlich verbesserte Kappa-Werte:
  - Satztyp: Erst↔LLM 0.623, Zweit↔LLM 0.768, Erst↔Zweit 0.737 (alle substanziell)
  - Taxonomie: Erst↔LLM 0.852, Zweit↔LLM 0.806, Erst↔Zweit 0.861 (substanziell bis fast perfekt)
  - Qualität: Erst↔Zweit 0.869 (fast perfekt), aber beide Annotatoren weichen vom LLM ab (0.350/0.401) — LLM bewertet systematisch strenger
- **Kap. 7 aktualisiert**:
  - Kappa-Tabelle mit allen 3 Paaren × 3 Dimensionen befüllt
  - Interpretation geschrieben (Taxonomie-Stärke, Satztyp-Abweichungen, Qualität-Diskrepanz LLM vs. Mensch)
  - Datenquellen-Tabelle mit echten Zahlen (585 Module, 5617 Sätze, 4 Hochschulen)
  - Datensatzstatistiken: Typ-Verteilung (92.1% K, 3.3% I, 4.5% S), Taxonomie-Verteilung, 31.5% Mehrfachzuordnung, Qualitätsverteilung
  - Unicode-Fehler (↔) durch LaTeX-Befehl ersetzt

### Literaturrecherche: LLMs als Texannotatoren
- **Ziel**: Wissenschaftliche Literatur zu LLM-basierter Textannotation recherchieren als Grundlage fuer die Methodik-Diskussion (LLM-Vorannotation + stratifizierte Validierung via Cohens Kappa)
- **Gefundene Schluesselpapers** (8 Stueck):
  1. Gilardi, Alizadeh & Kubli (2023) — PNAS: ChatGPT uebertrifft Crowd-Worker um ~25 Prozentpunkte Accuracy
  2. Toernberg (2023/2024) — arXiv/Social Science Computer Review: GPT-4 uebertrifft Experten bei politischer Tweet-Klassifikation
  3. Toernberg (2024) — Sociologica: Best Practices fuer LLM-Annotation (rigoroser Validierungsprozess)
  4. Pangakis, Wolken & Fasching (2023) — arXiv: 27 Tasks, Median-Accuracy 0.85, aber 9/27 Tasks mit Precision/Recall <0.5
  5. Reiss (2023) — arXiv: Krippendorffs Alpha unter 0.6 bei verschiedenen Temperatur-Settings
  6. Zhu et al. (2023) — arXiv: ChatGPT reproduziert menschliche Labels mit durchschnittlich 60.9% Accuracy
  7. Leitner & Rehm (2025) — JLCL: LLMs fuer deutsche Textklassifikation (5 Datensaetze, 13 Tasks)
  8. "To Err Is Human; To Annotate, SILICON?" (2024) — arXiv: Systematische Fehlerquellen bei LLM-Annotation
- **Ergebnis**: Detaillierte Zusammenfassung aller Papers mit Zitationen, Metriken und Relevanz fuer unseren Anwendungsfall erstellt

---

## 2026-06-22

### Literaturrecherche: Text Improvement Tools / Schreibassistenten
- **Ziel**: 3 relevante Paper für den Abschnitt "Verwandte Arbeiten" (Kap. 2) identifiziert, die automatisierte Textbewertung und Schreibunterstützung behandeln — thematisch analog zu unserem Kompetenzeditor
- **Gefundene Paper**:
  1. Fleckenstein, Liebenow & Meyer (2023): Meta-Analyse zu automatisiertem Feedback im Bildungskontext (Frontiers in AI)
  2. Chamoun, Schlichtkrull & Vlachos (2024): SWIF2T — Multi-Agenten-Tool für fokussiertes Feedback zu wissenschaftlichen Texten (ACL Findings)
  3. Naber (2003): Grundlagenarbeit zu LanguageTool — regelbasierter Stil- und Grammatik-Checker (Diplomarbeit Bielefeld)
- **Ergebnis**: Vollständige BibTeX-Einträge und Relevanzbegründungen erstellt; Paper decken Spektrum ab von regelbasiert (Naber) über ML-Meta-Analyse (Fleckenstein) bis LLM-basiert (Chamoun)

---

## 2026-05-13

### Loth/Konert-Prototyp auf Nuxt 4 portiert
- **Projekt**: `code_projects/kompetenzeditor/` (Nuxt 4.4.5, Vue 3.5, Vuetify 4.0.7, Tiptap 3.23, Dexie 4, Pinia 3)
- **Quellcode vollständig gelesen**: Alle 12 Dateien des alten Prototyps (`lot_kohnert_prototype/`) analysiert (~1600 Zeilen)
- **13 neue Dateien erstellt** in `app/`:
  - `nuxt.config.ts` — SSR deaktiviert, Vuetify-Transpile, Pinia-Modul, spaCy-Proxy-Config (Nitro devProxy), SCSS modern-compiler
  - `app/plugins/vuetify.js` — Vuetify 4 mit createVuetify, MDI-Icons, Light-Theme
  - `app/composables/useDatabase.js` — Dexie 4 mit exakt gleichen Verblisten (76 empfohlene Verben in 6 Taxonomiestufen, 6 schlechte Verben, 1 Modalverb, 2 Beispieltexte), CRUD-Operationen
  - `app/composables/useSpacy.js` — spaCy-Backend-Kommunikation via $fetch (POST /api/dep, /api/sents_dep)
  - `app/composables/useVerbAnalysis.js` — Verb-Matching-Logik, Highlight-Array-Aufbau (grün/rot/blau/grau)
  - `app/composables/useScoring.js` — Score-Berechnung (identische Formel wie Original)
  - `app/composables/useLevenshtein.js` — Levenshtein-Distanz (portiert, noch nicht aktiv genutzt)
  - `app/stores/editor.js` — Pinia-Store statt Vuex (currCompetenceID, lastSavedCompetenceID)
  - `app/layouts/default.vue` — Navigation-Drawer mit 3 Links, App-Bar mit Titel + Beta-Chip
  - `app/pages/index.vue` — Übersichtsseite mit Kompetenz-Karten (laden/löschen)
  - `app/pages/editor.vue` — Haupteditor mit Tiptap (statt ContentEditable), Bewertungssektion, Vorschläge-Panel
  - `app/pages/settings.vue` — Settings-Seite (Link zu spaCy-Test)
  - `app/pages/spacy.vue` — spaCy-Testseite (alle Endpoints)
- **API-Migrationen**:
  - Vue 2 Options API → Vue 3 Composition API mit `<script setup>`
  - Vuetify 2 → Vuetify 4 (v-list-item-content → Slots, depressed → variant="flat", solo → variant="solo", etc.)
  - ContentEditable-Overlay-Trick → Tiptap mit Custom Mark-Extension für Verb-Highlighting
  - Vuex → Pinia
  - $axios → $fetch (Nuxt 3 native)
  - Nuxt 2 Proxy → Nitro devProxy
- **Zusätzliche Dependencies installiert**: `@pinia/nuxt`, `@tiptap/core`
- **Hinweis**: `pnpm dev` konnte in dieser Session nicht verifiziert werden (Bash-Berechtigungslimit). Muss manuell getestet werden.

### Migration verifiziert und Bug gefixt
- **Problem**: Agent hatte `ssr: false` als Top-Level-Config gesetzt → verursacht in Nuxt 4 den Fehler "No entry found in rollupOptions.input"
- **Root Cause**: Nuxt 4 unterstützt `ssr: false` auf Top-Level nicht mehr für den Vite-Builder
- **Fix**: Ersetzt durch `routeRules: { '/**': { ssr: false } }` in `nuxt.config.ts`
- **Ergebnis**: Frisches Nuxt 4 Projekt erstellt, alle Dateien portiert, `pnpm dev` startet erfolgreich, HTML wird korrekt ausgeliefert (client-side rendering bestätigt)
- **Aufräumarbeiten**: Kaputtes Projekt (`kompetenzeditor_broken/`) entfernt

### Vuetify-Rendering gefixt
- **Problem**: Vuetify-Komponenten renderten ohne Styles, Icons zeigten als Textlabel
- **Ursache**: Plugin importierte keine Components/Directives (`import * as components from 'vuetify/components'`)
- **Fix**: `vuetify.js` Plugin um `components` und `directives` Imports ergänzt
- **Ergebnis**: UI rendert korrekt mit Icons, Cards, Navigation Drawer etc.

### Docker-Compose und spaCy-Orchestrierung
- **`docker-compose.yml`** erstellt: startet `bbieniek/spacyapi:de_v3` auf Port 8080 (wie Original-Prototyp)
- **API-Proxy** in `nuxt.config.ts` via `routeRules`: `/api/**` → `http://127.0.0.1:8080/**`
- **End-to-End verifiziert**: `docker compose up -d` + `pnpm dev` → spaCy-Dependency-Parsing funktioniert durch den Proxy
- Adressiert das IST-Analyse-Defizit "System ist nicht out-of-the-box reproduzierbar"

### Thesis-Text: Reproduzierbarkeit und Orchestrierung (Kap. 3.2)
- Neue Subsubsection `\subsubsection{Reproduzierbarkeit und Orchestrierung}` in `umsetzung.tex`
- Beschreibt Docker-Compose-Lösung für spaCy-Orchestrierung
- Erklärt, warum CI/CD nicht im Scope liegt, aber Composable-Architektur Testbarkeit ermöglicht

### Kompetenzeditor komplett neu aufgesetzt (Nuxt 4 + Tiptap 3)
- **Projekt komplett neu initialisiert** mit `nuxi init --template minimal` und `bun` als Package Manager
- **Stack**: Nuxt 4.4.5, Vue 3.5.34, Vuetify 4.0.7, Tiptap 3.23.4, Dexie 4.4.2, Pinia
- **16 Dateien erstellt** — vollständige Migration aller Features aus dem Original:
  - `nuxt.config.ts` — routeRules SSR-Deaktivierung, Nitro devProxy, Vite optimizeDeps
  - `app/plugins/vuetify.js` — Vuetify 4 mit vollständigem Component/Directives-Import
  - `app/composables/useDatabase.js` — Dexie 4 mit identischen Seed-Daten (76 Verben, 6 Taxonomiestufen)
  - `app/composables/useSpacy.js` — $fetch statt axios, Text-Sanitierung
  - `app/composables/useVerbAnalysis.js` — Verb-Matching + Highlight-Position-Berechnung mit Custom-Word-Boundaries (statt \b für Umlaute)
  - `app/composables/useScoring.js` — identische Formel, strukturiertes Return-Objekt
  - `app/extensions/verbHighlight.js` — ProseMirror Plugin mit Decoration.inline() und PluginKey-basiertem Transaction-Dispatch
  - `app/stores/editor.js` — Pinia statt Vuex
  - `app/layouts/default.vue` — Vuetify 3: `:rail` statt `:mini-variant`, `:prepend-icon`/`:title` statt `v-list-item-icon`/`-content`
  - `app/pages/index.vue` — Karten-Übersicht mit `v-bind="props"` Aktivator-Pattern
  - `app/pages/editor.vue` — Tiptap-Editor mit ProseMirror-Decorations, Promise.all für spaCy-Calls, korrigierte Save-Logik (add/update)
  - `app/pages/settings.vue` — spaCy Health-Check statt Link auf entfernte spacy.vue
  - `app/utils/levenshtein.js` — für zukünftige Embedding-Arbeit
- **Bugs des Originals behoben**: (1) Race-Condition bei parallelen spaCy-Calls → Promise.all, (2) Save immer nur add → jetzt add/update je nach compID
- **ContentEditable-Overlay-Hack ersetzt** durch Tiptap 3 mit ProseMirror Decorations — kein setContent() für Highlighting, Position-Mapping über doc.descendants()
- **Dev-Server startet erfolgreich** auf Port 3000, HTML wird korrekt ausgeliefert

---

## 2026-05-06

### Eigenleistung-Abschnitt korrigiert
- **Datei**: `thesis/chapters/einleitung.tex`, Abschnitt 1.5 (Eigenleistung)
- **Vorher**: "Der gesamte Quellcode wird im Rahmen dieser Arbeit neu entwickelt" — suggeriert Greenfield-Entwicklung
- **Nachher**: "Der bestehende Quellcode wird [...] auf aktuelle Technologieversionen migriert und um Embedding-basierte Analysefunktionen erweitert" — korrekt als Reengineering/Weiterentwicklung formuliert
- Begründung: Wir bauen auf dem Prototyp auf und modernisieren ihn, statt alles neu zu schreiben

### Template-Inhalte aus main.tex entfernt
- Gesamter Appendix entfernt: Formale Aspekte, Code Snippets, Generelle Hinweise, Zitier-Hinweise, Kolloquium-Hinweise
- Platzhalter-Texte in Kap. 2, 4, 5, 6 durch `\todo{}`-Marker ersetzt
- Kap. 2 Grundlagen: Subsections vorstrukturiert (Kompetenzbegriff, Bloom-Taxonomie, Sentence Embeddings, Related Work)
- Ergebnis: main.tex enthält nur noch die tatsächliche Thesis-Struktur

### EOL-Quellen und Nuxt-Abbildung eingebaut
- Drei BibTeX-Einträge für endoflife.date (Nuxt, Vue, Vuetify) in `literatur.bib`
- SVG-Grafik `figures/nuxtoutdated.svg` → PDF konvertiert mit rsvg-convert
- Abbildung in `umsetzung.tex` eingebunden (Abb. Nuxt Release-Zyklus) mit Quellenangabe
- Alle drei EOL-Quellen im Supplier-Stability-Absatz zitiert

### Vollständige IST-Analyse durchgeführt
- **Sommerville-Bewertung** Faktor für Faktor mit Felix validiert (14 Faktoren aus Fig. 9.10/9.11)
- **IST-SOLL-Abgleich**: Alle 11 Anforderungen (FA1–FA6, NFA1–NFA5) gegen Prototyp geprüft → 4 erfüllt, 4 teilweise, 3 nicht erfüllt
- **Loth/Konert-Limitationen** aus DELFI-Paper + Masterprojekt-Bericht extrahiert (8 Punkte L1–L8), auf Anforderungen gemappt
- **Strategische Einordnung**: Reengineer (hoher Geschäftswert × niedrige techn. Qualität)
- **Hevner**: Übergeordneter Forschungsrahmen (Build+Evaluate), nicht direkt für IST-Analyse relevant — Sommerville liefert das Wie
- Alles dokumentiert in `docs/results.md` §8

### IST-Analyse als LaTeX-Kapitel geschrieben (Rewrite)
- **Datei**: `thesis/chapters/umsetzung.tex` — vollständig neu geschrieben
- **Erste Version** war tabellenbasiert (drei große Tabellen mit allen Details in Zellen) — von Felix als zu checklistenartig und nicht akademisch genug abgelehnt
- **Rewrite**: Fließtext für Sommerville-Bewertung und IST-SOLL-Abgleich, nur eine kompakte Übersichtstabelle (ID, Anforderung, Typ, Status) ohne Detailbeschreibungen in Zellen
- LaTeX-Formatierungsregeln aus Template-Kapitel "Formale Aspekte" als Memory gespeichert (`feedback_latex_rules.md`)
- Caption vor Centering, Label in Caption, korrekte Referenzkonventionen (Tab.~\ref, Kap.~\ref)

### Sommerville (Kap. 9 Software Evolution) für IST-Analyse aufbereitet
- **Quelle**: Sommerville, Ian (2016): Software Engineering, 10. Aufl., Kap. 9 (S. 255–280)
- **Relevante Konzepte extrahiert und auf Prototyp angewendet** → `docs/results.md` §8
  - Legacy-System-Bewertung (Fig. 9.10/9.11): Umgebungs- und Anwendungsfaktoren systematisch auf den Loth/Konert-Prototyp angewendet
  - Strategische Entscheidung: Reengineering (nicht Scrap/Maintain/Replace) — hoher Geschäftswert, aber veralteter Stack
  - Drei Wartungstypen: Unsere Arbeit = Environmental Adaptation (Nuxt 2→4) + Functionality Addition (Embedding-Features)
  - Reengineering-Prozess (Fig. 9.14): 5 Aktivitäten auf unseren Kontext übertragen
- **BibTeX-Eintrag**: `sommerville2016software` in `thesis/literatur.bib` hinzugefügt
- **Verwendung**: Rahmen für die systematische IST-Analyse des Prototyps in Kapitel 3 (Umsetzung)

---

## 2026-04-25

### Embedding-Modell-Evaluierung und -Entscheidung
- **3 Kandidaten-Modelle** systematisch auf unseren 3213 Sätzen evaluiert: `code_projects/evaluate_embeddings.py`
  - paraphrase-multilingual-MiniLM-L12-v2 (384d, 1859 Sätze/s)
  - deutsche-telekom/gbert-large-paraphrase-cosine (1024d, 203 Sätze/s)
  - T-Systems-onsite/cross-en-de-roberta-sentence-transformer (768d, 546 Sätze/s)
- **Methodik**: SVM (RBF, C=10) auf Train-Split (2572), evaluiert auf Test-Split (641)
- **Ergebnis**: T-Systems cross-en-de-roberta gewinnt deutlich
  - Taxonomie-Klassifikation (6 Klassen): **F1 0.906** (vs. 0.875 gbert, 0.846 MiniLM)
  - Typ-Klassifikation (K/I/S): F1 0.977 (alle Modelle gleichauf bei ~98%)
  - Beste Einzelwerte: Erinnern 0.944, Verstehen 0.907, Anwenden 0.918, Analysieren 0.864, Bewerten 0.867, Erschaffen 0.878
- **Entscheidung dokumentiert**: `docs/modellentscheidung_embedding.md`
- **Hinweis**: aari1995/German_Semantic_STS_V2 (bester STS-Benchmark) crashte unter Python 3.14 — konnte nicht getestet werden
- Python-venv eingerichtet: `.venv/` mit sentence-transformers, scikit-learn, torch

### Architekturentwurf erstellt
- **Gesamtarchitektur** dokumentiert: `docs/architektur.md`
  - 2-Komponenten-System: Frontend (Nuxt 4) + Backend (Python/FastAPI)
  - Entscheidung Backend-API statt Browser-ONNX (Modell zu groß mit 278M Params)
  - 6-Schritte Hybrid-Pipeline: Segmentierung → spaCy → Regelbasiert → SBERT+SVM → Ähnlichkeitssuche → Aggregation
  - Cascading-Logik: Eindeutige Verben → Regel (Konfidenz 0.95); mehrdeutige/unbekannte → Embedding+SVM
  - API-Design: POST /api/analyze mit JSON Request/Response
  - Performance-Abschätzung: ~10ms/Satz, ~50-100ms für typischen Modultext (weit unter 2s-Anforderung)
- **Nuxt-4-Migration**: Neuaufbau statt inkrementelle Migration (Vue 2→3, Vuetify 2→3, ContentEditable→Tiptap betreffen praktisch jede Zeile)
- **Geplante Projektstruktur**: backend/ (FastAPI + Pipeline) + frontend/ (Nuxt 4 + Tiptap)
- Verbliste: Zusammenführung Prototyp (76 Verben) + HRK nexus, bereinigt um Bug (`Zusammenhänge` kein Verb), mehrdeutige Verben explizit modelliert

### Manuelle Validierung abgeschlossen
- Stichprobenartige Prüfung der LLM-Annotationen bestätigt hohe Qualität
- Entscheidung: LLM-Annotationen als Ground Truth übernehmen (kein extensives manuelles Korrigieren nötig)
- Train/Test-Split (80/20, stratifiziert, Seed 42) in `data/qualifikationsziele_annotiert.csv` hinzugefügt

### TikZ-Architekturdiagramme erstellt
- **Gesamtarchitektur**: `thesis/figures/architektur_gesamt.tex` — 4 Farbgruppen (Frontend blau, Backend orange, Modelle grün, Referenz-DB violett), Palatino-Font passend zur Thesis-Vorlage
- **Cascading-Pipeline**: `thesis/figures/architektur_cascading.tex` — 6-Schritte-Flowchart mit Entscheidungsknoten (Verbliste/Negativliste), zwei Ergebnispfaden (regelbasiert/embedding-basiert)
- Beide als standalone TikZ-Dokumente, direkt per `\includegraphics` einbindbar

### Kapitel 1 (Einleitung) vollständig geschrieben
- **Datei**: `thesis/chapters/einleitung.tex`, eingebunden via `\input` in `main.tex`
- **5 Subsections**: Kontext (Bologna, Kompetenzorientierung), Problemstellung und Motivation (Grenzen regelbasiert + datengetrieben, Forschungslücke, Forschungsfrage), Ziele der Arbeit (4 quantifizierbare Ziele), Eigenleistung (Loth/Konert-Prototyp als Vorarbeit), Aufbau der Arbeit
- Alle Zitate referenzieren `literatur.bib`-Keys, kompiliert fehlerfrei mit pdflatex+bibtex
- Titelseite in `main.tex` aktualisiert (Titel, Masterarbeit, Name, Betreuer)

---

## 2026-04-07

### Gold-Standard-Annotation: Schema + LLM-Vorannotation
- **Annotationsleitfaden** erstellt: `docs/annotationsleitfaden.md`
  - 3 Satztypen (K/I/S), 6 Taxonomiestufen, 10 Entscheidungsregeln, Grenzfall-Konventionen
  - 3-Phasen-Prozess: LLM-Vorannotation → manuelle Validierung (250-300 Sätze) → Inter-Annotator κ
- **LLM-Vorannotation** aller 3213 Sätze mit Claude Sonnet: `code_projects/vorannotation.py`
  - Ergebnis: 3039 K (94.6%), 67 I (2.1%), 107 S (3.3%)
  - Taxonomie: Stufe 3 dominiert (35.2%), gefolgt von Stufe 2 (18.1%) und Stufe 1 (16.2%)
  - Mittlere Konfidenz: 0.82; nur 171 Sätze (5.3%) unter 0.7 → Priorität für manuelle Validierung
  - Output: `data/qualifikationsziele_annotiert.csv`

### Qualifikationsziele aus Modulhandbüchern extrahiert
- **15 PDF-Modulhandbücher** (FBAI HS Fulda) automatisiert verarbeitet
- Extraktions-Script: `code_projects/extract_qualifikationsziele.py` (v6, seitenbasiert)
- **Ergebnis: 699 Module, 3213 Sätze, 15 Studiengänge** → `data/qualifikationsziele.csv`
- Technische Herausforderungen gelöst:
  - PyMuPDF statt pdfplumber (Python 3.14 Kompatibilität)
  - Seitenbasierte Extraktion statt Volltext-Suche (PyMuPDF extrahiert Modul-ID als separaten Textblock am Seitenende/-anfang je nach PDF-Vorlage)
  - "Die Studierenden …"-Header-Erkennung mit Sentinel-Markern (§H§) vor Line-Joining
  - Abkürzungsschutz (z.B., u.a., etc.) für korrekte Satzsegmentierung
  - Filter für Header-Sätze ("sind in der Lage:", "Die Teilnehmenden sind in der Lage")
- 528/3213 Sätze (16%) beginnen mit Kleinbuchstabe — legitime Infinitivkonstruktionen aus ET/LT-Modulen ("...zu verstehen", "...anzuwenden")
- Dient als Referenzdatenbank für FA3 (Ähnlichkeitsempfehlungen) und Gold-Standard-Basis

### Anforderungserhebung abgeschlossen
- Neue Datei `docs/anforderungen.md` erstellt
- **6 funktionale Anforderungen (FA1–FA6):** Klassifikation, Taxonomie-Zuordnung, Empfehlungen, Set-Analyse, Echtzeit-Feedback, Persistenz
- **5 nicht-funktionale Anforderungen (NFA1–NFA5):** Konfidenzmaße, Transparenz, Deutsche Sprache, Technologie-Migration (Nuxt 4), Performance
- **MoSCoW-Priorisierung:** 5 Must-have (Klassifikation, Taxonomie, Echtzeit, Konfidenz, Deutsch), 4 Should-have, 2 Could-have, 4 Won't-have
- **Quellen-Mapping:** Jede Anforderung systematisch auf Prototyp-Schwächen (S1–S8), Konert-Feedback (K1–K5) und Literatur zurückgeführt
- **Hybrid-Cascading-Entwurf:** 4-Schritt-Logik (spaCy → Regelcheck → Embedding → Klassifikation) als ASCII-Diagramm dokumentiert
- Wochen 1–3 (plan.md) vollständig abgeschlossen; Anforderungserhebung aus Wochen 4–5 ebenfalls erledigt

### Prototyp vollständig lauffähig (spaCy-Docker)
- spaCy-Docker-Image `bbieniek/spacyapi:de_v3` gepullt und gestartet (Port 8080)
- Prototyp jetzt vollständig funktional auf localhost:3000 mit Backend-Anbindung

---

## 2026-03-17

### Papers inhaltlich durchgearbeitet — Kernaussagen für Kap. 2
- **23 PDFs** aus 5 Bereichen systematisch gelesen und Kernaussagen extrahiert
- Kompetenzbegriff: Schaper Umsetzungsdefizite (S. 28), Klieme Kompetenzmodelle (S. 75), KMK Bloom+HQR (S. 5), DQR Handlungskompetenz (S. 15)
- Taxonomien: Krathwohl Zweidimensionalität (S. 213), Stanny 176 Verben mit massiven Überlappungen, Cursio deutsche Verblisten-Warnung (S. 8)
- Embeddings: BERT→SBERT→Multilingual SBERT→E5→M3; SBERT-Kerninsight: naive BERT-Embeddings schlechter als GloVe
- Verwandte Arbeiten: Li F1=0.95, Kumar SVM>BERT bei kleinen Daten, Huber Transfer-Problem, Chiticariu 67% kommerzielle IE regelbasiert
- Methodik: Hevner 7 Guidelines + HRK Qualitätskriterien
- Ergebnisse in docs/results.md §1–6 konsolidiert

### Arbeitsdefinition „Kompetenzformulierung" festgelegt
- Satz mit (a) Studierenden als Subjekt, (b) beobachtbarem Handlungsverb, (c) Gegenstand
- Hergeleitet aus HRK nexus, Krathwohl, Cursio/Jahn, Kopf et al., Weinert/Schaper
- Eingetragen in docs/results.md §1.3

### Prototyp vollständig lauffähig (inkl. spaCy-Backend)
- spaCy-Docker-Container gestartet (`bbieniek/spacyapi:de_v3`, Port 8080)
- package.json auf `nuxt: ^2.18.1` korrigiert

### Wochen 1–3 komplett abgeschlossen
- Alle Checkboxen in docs/plan.md abgehakt (Literatur 6/6, Prototyp 4/4, Begriffsabgrenzung 2/2)

---

## 2026-03-11

### Vollständige Prototypanalyse (Loth & Konert 2022)
- Alle Quelldateien gelesen (~1.600 Zeilen Code, davon ~1.300 in editor.vue)
- **Nuxt-Version-Problem entdeckt:** package.json deklariert Nuxt 3.12.4, Code ist komplett Nuxt 2. Downgrade auf `nuxt@2` nötig für Start.
- Prototyp erfolgreich gestartet (Nuxt 2 auf localhost:3000). spaCy-Backend (Docker, Port 8080) fehlt im Repo.
- **Analyse-Pipeline dokumentiert:** 4 Schritte (Texteingabe → spaCy-Tokenisierung → Verb-Abgleich gegen 80er-Liste → Score-Berechnung)
- **10 Bugs/Probleme identifiziert:** u.a. „Zusammenhänge" als Verb, Duplikat „erkennen" in 3 Stufen, Memory-Leak in fillHighlight(), ungenutzter Code (Levenshtein, Einleitungen, nlpNouns/nlpAdjectives)
- **8 systematische Schwächen katalogisiert (S1–S8):** Exakter Stringvergleich, geschlossene Verbliste, keine Kontextsensitivität, keine Klassifikation, statische Empfehlungen, keine Set-Analyse, simplifizierter Score, kein Konfidenzmaß
- **Wiederverwendbarkeits-Assessment:** Verbliste (80 Einträge + Taxonomie) wertvollster Bestandteil; UI-Konzept (3 Panels) übertragbar; Nuxt-2-Code und Vuetify-2-Komponenten nicht migrierbar
- Ergebnisse in docs/results.md §5 (erweitert von 25 auf ~150 Zeilen), plan.md alle 4 Prototyp-Checkboxen abgehakt

### Weinert OCR-Transkription
- PDF (Scan) von Weinert (2001/2002) als `.pdf.md` vorhanden (externer OCR-Dienst)
- Kompetenzdefinition auf S. 27–28 verifiziert, Kompetenzklassen (fachlich, fachübergreifend, Handlung) auf S. 28–29

### literatur.bib verifiziert und korrigiert
- Alle 23 PDFs gegen Originale und Online-Quellen geprüft (4 parallele Agenten)
- **Kritische Fehler behoben:** Loth heißt Ludwig (nicht Alexander), Titel beider Loth-Einträge korrigiert, Li et al. (2022) hatte komplett falsche Autoren
- **PDF-Verwechslungen entdeckt:** `Ogunleye_2021` enthält tatsächlich Banujan et al. (2023), `Abdellatif_2025` enthält Kumar et al. (2025) — Bib-Einträge auf tatsächliche Inhalte aktualisiert
- **Weitere Korrekturen:** DQR-Herausgeber (Bund-Länder-Koordinierungsstelle statt AK DQR), Cursio Jahr 2013 statt 2014, Chen 2024 in Findings of ACL (nicht Hauptkonferenz), Kopf et al. von @incollection zu @book, Weinert Jahr→2002 (2. Auflage)
- DOIs ergänzt bei: Krathwohl, Stanny, Reimers (2x), Devlin, Chen, Loth, Li, Chiticariu

### UEBERSICHT.md aktualisiert
- Alle Korrekturen aus Bib-Verifikation übernommen
- Irreführende Dateinamen (Ogunleye, Abdellatif) als ⚠️ markiert

### results.md erstellt
- Konsolidierte Ergebnisse aller erledigten Plan-Schritte in `docs/results.md`
- 8 Abschnitte: Kompetenzbegriff, Taxonomien, Embeddings, Verwandte Arbeiten, Prototyp, Methodik, Konert-Feedback, Offene Fragen
- Verifizierte Originalzitate mit Seitenzahlen aus Weinert (S. 27–28), Schaper (S. 14, 28–29), HRK nexus (S. 2), Kopf et al. (S. 3–5)
- Schaper-Synthese-Definition (S. 29) und drei Kompetenzverständnisse (S. 28) ergänzt

### E-Mail-Entwurf an Konert
- Korrigierte Version erstellt (alte hatte Hybrid fälschlich als "Kern der Arbeit" beschrieben)
- Alle 5 Konert-Punkte als Fließtext eingearbeitet

---

## 2026-03-10

### CLAUDE.md aktualisiert
- Projektbeschreibung auf aktuellen Stand gebracht (Titel, Forschungsfrage, Zeitplan, Tech-Details)
- Memory-Dateien für Cross-Session-Persistenz eingerichtet

### Exposé-Analyse: Machbarkeit und Subschritte
- Alle 8 Zeitplan-Phasen in konkrete Subschritte zerlegt
- Risiken identifiziert: Nuxt-4-Migration als eigenes Projekt, Gold-Standard-Annotation als externe Abhängigkeit, 4×3 Evaluationsmatrix
- Empfehlungen: Gold-Standard früher beginnen, Nuxt-4-Migration minimal halten, Set-Analyse als Nice-to-have, zweite Annotationsperson jetzt ansprechen

### Exposé: LaTeX-Kompilierung
- Fehlende TeX-Pakete installiert (texlive-langgerman, texlive-latexextra, texlive-fontsrecommended)
- PDF erfolgreich erzeugt (5 Seiten, keine Fehler, nur Underfull-hbox-Warnungen in Zeitplan-Tabelle)
- Zitationen geprüft: alle 9 \cite-Keys haben passende \bibitem-Einträge

### Literaturrecherche: Kompetenzbegriff in der deutschen Hochschullehre

Strukturierte Aufarbeitung der zentralen Definitionen und Rahmenwerke zum Kompetenzbegriff. Quellen: lokale PDFs (HRK nexus 2015, Loth/Konert 2022) sowie Trainingswissen zu Weinert, Schaper, KMK, Bologna/EQR/DQR. **Hinweis:** WebSearch und WebFetch waren nicht verfuegbar; Weinert- und Schaper-Inhalte basieren auf Trainingswissen und muessen anhand der Originalquellen verifiziert werden.

#### 1. Weinert (2001) -- Kompetenzdefinition

**Quelle:** Weinert, F. E.: Vergleichende Leistungsmessung in Schulen -- eine umstrittene Selbstverstaendlichkeit. In: Weinert (Hrsg.): Leistungsmessungen in Schulen. Beltz, S. 17-32, 2001.

**Kernaussage:** Weinert definiert Kompetenzen als "die bei Individuen verfuegbaren oder durch sie erlernbaren kognitiven Faehigkeiten und Fertigkeiten, um bestimmte Probleme zu loesen, sowie die damit verbundenen motivationalen, volitionalen und sozialen Bereitschaften und Faehigkeiten, um die Problemloesungen in variablen Situationen erfolgreich und verantwortungsvoll nutzen zu koennen." Die Definition betont drei Dimensionen: (1) kognitive Faehigkeiten (Wissen, Koennen), (2) motivationale/volitionale Aspekte und (3) soziale Bereitschaften. Kompetenzen sind laut Weinert erlernbar, situationsuebergreifend anwendbar und auf verantwortungsvolles Handeln ausgerichtet.

**Bestaetigung aus Loth/Konert (2022):** Der Artikel referenziert [We01] direkt und fasst zusammen: "Laut dieser umfassen Kompetenzen: Wissen, Koennen, sowie motivationale und soziale Aspekte. Kompetenzen werden im Verlauf des Bildungsprozesses von Lernenden erworben und koennen spaeter nachgewiesen werden."

**Relevanz fuer die Thesis:** Weinert ist die Standardreferenz fuer den Kompetenzbegriff im deutschsprachigen Bildungskontext. Der Loth/Konert-Prototyp und damit auch diese Masterarbeit bauen explizit auf dieser Definition auf.

#### 2. Schaper et al. (2012) -- Fachgutachten zur Kompetenzorientierung

**Quelle:** Schaper, N. (unter Mitwirkung von Reis, O.; Wildt, J.; Horvath, E.; Bender, E.): Fachgutachten zur Kompetenzorientierung in Studium und Lehre. HRK nexus, Bonn 2012.

**Kernaussagen:**
- Das Gutachten definiert ein akademisch orientiertes Kompetenzverstaendnis, das ueber Weinerts schulbezogene Definition hinausgeht.
- Kompetenz wird als Befaehigung verstanden, "in bestimmten Anforderungsbereichen angemessen, verantwortlich und erfolgreich zu handeln."
- Diese Befaehigung umfasst ein "integrierendes Buendel von komplexem Wissen, Fertigkeiten, Faehigkeiten, motivationalen Orientierungen und (Wert-)Haltungen."
- Akademische Kompetenzen zeichnen sich zusaetzlich aus durch: Befaehigung zur Anwendung wissenschaftlicher Konzepte auf komplexe Anforderungskontexte, zur wissenschaftlichen Analyse und Reflexion, zur anschlussfaehigen Kommunikation von Wissensbestaenden und -methoden, sowie zur Selbstregulierung des eigenen problemloesungs- und erkenntnisgeleiteten Handelns.
- Das Gutachten empfiehlt die systematische Verankerung von Kompetenzorientierung in Curricula, Lehre und Pruefung.

**Bestaetigung aus HRK nexus (2015):** Die nexus-Publikation referenziert Schaper direkt und uebernimmt dessen Kompetenzverstaendnis als Grundlage (S. 2: "in Anlehnung an Schaper 2012").

**Relevanz fuer die Thesis:** Schaper liefert das akademische Kompetenzmodell, das die Basis fuer die Analyse von Modulhandbuch-Formulierungen bildet. Die drei Elemente (Befaehigung + Buendel + akademische Spezifika) sind zentral fuer die Klassifikation.

#### 3. HRK nexus (2015) -- "Lernergebnisse praktisch formulieren"

**Quelle:** HRK nexus Impulse fuer die Praxis, Ausgabe 2, Neuauflage Juni 2015. Lokal vorhanden: `materials/Lernergebnisse praktisch formulieren.pdf`

**Kernaussagen:**
- Lernergebnisse beschreiben, "was ein Lernender nach Abschluss eines Lernprozesses weiss, versteht und in der Lage ist zu tun/vorzufuehren."
- Lernergebnisse werden in zwei Dimensionen beschrieben: (1) fach-/wissensbezogener Inhalt und (2) Beschreibung dessen, was mit oder an den Inhalten gemacht werden soll.
- Basis der Lernergebnisse sind die Kompetenzen, die von Studierenden erworben werden sollen.
- Empfohlene Satzschablone: "Bei Abschluss des Lernprozesses wird der erfolgreiche Student in der Lage sein, ..."
- **Leitlinien fuer die Formulierung:**
  - Nur ein Verb je Lernergebnis plus Kontext
  - Keine vagen Begriffe; keine Verben, die Lehrziele beschreiben
  - Ein Satz je Lernergebnis
  - Lernergebnisse muessen feststell- und messbar sein
  - Lernergebnisse muessen beurteilbar sein
  - Lernergebnisse muessen im verfuegbaren Zeitrahmen erreichbar sein
  - Lernergebnisse sollen auf allen Stufen der Bloomschen Taxonomie angesiedelt sein
- Die Publikation stellt die kognitive Taxonomie nach Anderson/Krathwohl (2001) mit 6 Stufen und zugehoerigen Verblisten dar, sowie die affektive Taxonomie nach Bloom/Krathwohl.
- Praktischer 9-Schritte-Prozess: Vorwissen -> Lehr-/Lernziele -> Niveaustufen -> Taxonomie -> Formulieren -> Lehrmethode -> Pruefungsform -> Workload.

**Relevanz fuer die Thesis:** Diese Publikation ist die unmittelbare Praxisgrundlage fuer die Qualitaetskriterien im Editor-Prototyp. Die Verblisten und die Satzstruktur-Empfehlungen sind genau das, was der regelbasierte Ansatz prueft -- und was der Embedding-Ansatz erweitern soll.

#### 4. Abgrenzung: Lernziel vs. Lernergebnis vs. Kompetenzziel

| Begriff | Definition | Perspektive | Beispiel |
|---------|-----------|-------------|---------|
| **Lernziel** (Learning Objective) | Beschreibt, was Lehrende mit einer Veranstaltung beabsichtigen; umfasst inhaltlich-fachliches Wissen (Fachkompetenz) sowie Methoden-, Sozial- und Personalkompetenz. | **Lehrenden-Perspektive** (Input-orientiert) | "Den Studierenden die Grundlagen des Voelkerrechts vermitteln." |
| **Lernergebnis** (Learning Outcome) | Beschreibt, was Studierende nach Abschluss eines Lernprozesses wissen, verstehen und tun koennen. Besteht aus Inhalt + beobachtbarer Handlung (Verb). | **Studierenden-Perspektive** (Output-orientiert) | "Die Studierenden koennen die grundlegenden Prinzipien des Voelkerrechts darstellen und erklaeren." |
| **Kompetenzziel** | Uebergreifende Befaehigung, die durch mehrere Lernergebnisse operationalisiert wird. Umfasst Wissen, Fertigkeiten und Haltungen als integriertes Ganzes. | **Befaehigungs-Perspektive** (ganzheitlich) | "Fachkompetenz im Voelkerrecht auf Analysestufe." |

**Zentrale Unterscheidung (aus HRK nexus 2015, S. 2):** "Von den Lernergebnissen sind Lehr- und Lernziele zu unterscheiden." Der Bologna-Prozess hat den Paradigmenwechsel von der Input-Orientierung (was wird gelehrt?) zur Output-Orientierung (was koennen Studierende?) vorangetrieben. Lernergebnisse sind die operationalisierte Form von Kompetenzzielen.

**Relevanz fuer die Thesis:** Die Klassifikations-Dimension des Prototyps muss genau diese Unterscheidung treffen: Ist ein Satz eine Kompetenzformulierung (= Lernergebnis mit beobachtbarem Verb) oder eine reine Inhaltsbeschreibung (= Input-orientiertes Lernziel)?

#### 5. Weitere relevante Definitionen und Rahmenwerke

**a) KMK (Kultusministerkonferenz, 2017) -- Qualifikationsrahmen fuer deutsche Hochschulabschluesse:**
- Definiert Kompetenzprofile fuer Bachelor, Master und Promotion.
- Unterscheidet zwischen Wissen und Verstehen (Fachkompetenz) sowie Koennen (instrumentale, systemische und kommunikative Kompetenzen).
- Bachelor: breites Grundlagenwissen, Faehigkeit zur Problemloesung im Fachgebiet.
- Master: vertieftes/spezialisiertes Wissen, Faehigkeit zur eigenstaendigen Forschung.

**b) Bologna-Prozess (1999ff.):**
- Einfuehrung der Outcome-Orientierung als zentrales Prinzip europaeischer Hochschulbildung.
- Shift from Teaching to Learning: Nicht mehr der Lehrinhalt, sondern die nachweisbaren Lernergebnisse stehen im Zentrum.
- Die Dublin Descriptors (2004) definieren generische Kompetenzniveaus fuer Bachelor/Master/PhD.

**c) EQR/DQR (Europaeischer/Deutscher Qualifikationsrahmen):**
- EQR (2008): 8 Niveaustufen, beschrieben durch Kenntnisse, Fertigkeiten und Kompetenz (im Sinne von Verantwortung/Selbststaendigkeit).
- DQR (2011): Deutsche Umsetzung des EQR. Unterscheidet zwei Kompetenzkategorien:
  - **Fachkompetenz:** Wissen (Tiefe, Breite) + Fertigkeiten (instrumentale/systemische Fertigkeiten, Beurteilungsfaehigkeit)
  - **Personale Kompetenz:** Sozialkompetenz + Selbststaendigkeit
- Bachelor = DQR-Niveau 6, Master = DQR-Niveau 7.
- Der DQR-Kompetenzbegriff ist breiter als Weinerts kognitiv fokussierte Definition und schliesst explizit Sozial- und Personalkompetenz ein.

**d) Klieme et al. (2003) -- Expertise zu Bildungsstandards:**
- Erweitert Weinerts Definition fuer den schulischen Kontext.
- Kompetenzen sind kontextspezifisch, erlernbar, durch Erfahrung und Uebung erworben.
- Wird in Loth/Konert (2022) als [Kl03] referenziert.

#### Zusammenfassung und Implikationen fuer die Masterarbeit

Die Definitionen bilden eine klare Hierarchie:
1. **Weinert (2001)** liefert die psychologisch fundierte Basisdefinition (Wissen + Koennen + Motivation + Soziales).
2. **Schaper (2012)** adaptiert dies fuer den akademischen Kontext (+ wissenschaftliche Analyse, Reflexion, Kommunikation).
3. **HRK nexus (2015)** operationalisiert dies fuer die Praxis der Modulhandbuch-Erstellung (Verblisten, Satzschablonen, Taxonomiestufen).
4. **KMK/DQR** gibt den ordnungspolitischen Rahmen vor (Niveaustufen, Kompetenztypen).

Fuer den Embedding-Ansatz der Thesis ergeben sich daraus konkrete Anforderungen:
- Die **Klassifikation** (Kompetenzformulierung vs. Inhaltsbeschreibung) muss den Unterschied zwischen Output- und Input-Orientierung erfassen.
- Die **Taxonomie-Zuordnung** muss ueber starre Verblisten hinausgehen und semantische Naehe zu den Anderson/Krathwohl-Stufen erkennen.
- Die **Empfehlungen** sollten die HRK-nexus-Leitlinien als Qualitaetskriterien operationalisieren.
- Die **Set-Analyse** muss pruefen, ob ein Modul verschiedene Taxonomiestufen und Kompetenztypen (Fach-, Methoden-, Sozial-, Personalkompetenz) abdeckt.

**Offene Aufgaben:**
- Originaltext Weinert (2001) beschaffen und exaktes Zitat verifizieren
- Schaper et al. (2012) Volltext beschaffen (PDF ueber HRK-nexus-Seite)
- KMK-Qualifikationsrahmen (2017) Volltext beschaffen
- DQR-Handbuch (2011/2021) beschaffen
- Pruefen, ob weitere Quellen aus HRK-nexus-Literaturliste relevant sind (insb. Kennedy 2006, Bachmann 2011)

### Recherche: Sentence-BERT und Embedding-Modelle fuer deutsche Texte

Strukturierte Aufarbeitung von Sentence-BERT-Grundlagen, verfuegbaren deutschen/multilingualen Modellen und praktischen Aspekten fuer die Implementierung. Quellen: HuggingFace Model Cards (direkt abgerufen), Trainingswissen zu Sentence-BERT (Paper arXiv:1908.10084). **Hinweis:** WebSearch war nicht verfuegbar; arxiv-Zugriff war blockiert. Modell-Benchmarks stammen direkt von den HuggingFace Model Cards.

#### 1. Sentence-BERT (Reimers & Gurevych, 2019) -- Grundlagen

**Kernidee und Motivation:**
- Standard-BERT erfordert fuer Satzaehnlichkeit das paarweise Einspeisen aller Satzkombinationen (bei 10.000 Saetzen: ~50 Mio. Inferenzen, ca. 65 Stunden). SBERT reduziert dies auf Sekunden durch vorberechnete Embeddings.
- SBERT modifiziert BERT mit einer Siamese/Triplet-Network-Architektur, um feste Satz-Embeddings zu erzeugen, die per Cosinus-Aehnlichkeit verglichen werden koennen.

**Architektur (Siamese Network):**
- Zwei identische BERT-Instanzen teilen sich die Gewichte (weight-sharing).
- Jeder Satz wird einzeln durch BERT geschickt.
- Ueber den Token-Ausgaben wird ein Pooling angewendet.
- Die resultierenden festen Vektoren werden verglichen (Cosinus-Aehnlichkeit, Manhattan, Euklidisch).

**Pooling-Strategien:**
- MEAN-Pooling (Durchschnitt aller Token-Embeddings) -- beste Ergebnisse laut Paper
- CLS-Token (nur [CLS]-Vektor)
- MAX-Pooling (Maximum ueber alle Token)

**Training:**
- Objective 1 -- Classification (NLI): Softmax ueber Konkatenation (u, v, |u-v|)
- Objective 2 -- Regression (STS): Cosine Similarity Loss
- Trainingsdaten: SNLI (570k) + MultiNLI (430k) fuer NLI; STSbenchmark fuer Regression

**Paper:** arXiv:1908.10084

#### 2. Verfuegbare Modelle fuer Deutsche Texte (HuggingFace)

| Modell | Basis | Dim. | Params | Deutsch-STS (Spearman) | Besonderheiten |
|--------|-------|------|--------|------------------------|----------------|
| paraphrase-multilingual-MiniLM-L12-v2 | BERT (MiniLM) | 384 | ~118M | ~0.82 (geschaetzt) | 50 Sprachen, sehr schnell, ONNX-faehig, 23M+ Downloads/Monat |
| paraphrase-multilingual-mpnet-base-v2 | XLM-RoBERTa | 768 | ~278M | 0.8355 | 50 Sprachen, hoehere Qualitaet als MiniLM |
| T-Systems/cross-en-de-roberta-sentence-transformer | XLM-RoBERTa | 768 | ~278M | **0.8550** | Speziell DE/EN, cross-lingualer Score 0.8525 |
| aari1995/German_Semantic_STS_V2 | deepset/gbert-large | 1024 | ~335M | **0.8626** | Bester reiner Deutsch-STS-Score |
| deutsche-telekom/gbert-large-paraphrase-cosine | deepset/gbert-large | 1024 | ~335M | k.A. (gut fuer Few-Shot) | Optimiert fuer SetFit/Few-Shot-Klassifikation |
| deepset/gbert-large | BERT (deutsch) | 1024 | ~335M | (Basismodell, kein ST) | Muss fuer STS fine-getuned werden |
| deepset/gbert-base | BERT (deutsch) | 768 | ~110M | (Basismodell) | Kleiner, schneller |

#### 3. Benchmarks: Deutsche Semantische Aehnlichkeit (German STS)

**Ranking nach German-STS Spearman-Korrelation (STSbenchmark deutsch):**
1. **aari1995/German_Semantic_STS_V2**: 0.8626
2. **T-Systems cross-en-de-roberta**: 0.8550
3. **german-roberta-sentence-transformer-v2**: 0.8529
4. **paraphrase-multilingual-mpnet-base-v2**: 0.8355
5. **xlm-r-distilroberta-base-paraphrase-v1**: 0.8079

Die Unterschiede zwischen den Top-3-Modellen sind gering (~0.01). Fuer den Anwendungsfall "Kompetenzformulierungen" koennte domaenenspezifisches Finetuning wichtiger sein als die Modellwahl unter den Top-Kandidaten.

#### 4. Neuere Modelle (2023-2025)

**intfloat/multilingual-e5-large (2023):**
- 0.6B Params, 1024 Dim., 100 Sprachen, XLM-RoBERTa-large-basiert
- Erfordert Praefixe: "query: " / "passage: "
- Training: 2-stufig (schwache Supervision auf 5B Paaren, dann ueberwachtes Finetuning)
- Sehr starke Retrieval-Performance (MRR@10 avg: 70.5 ueber Mr. TyDi)

**BAAI/bge-m3 (2024):**
- 100+ Sprachen, 1024 Dim., bis zu 8192 Tokens, MIT-Lizenz
- Drei Retrieval-Modi: Dense, Sparse (lexikalisch), Multi-Vector (ColBERT)
- 17.7M Downloads/Monat -- aktuell populaerstes multilinguales Embedding-Modell
- Hybrid-Retrieval (dense + sparse) besonders stark
- Interessant fuer die Thesis: Sparse-Retrieval koennte regelbasierte Analyse konzeptionell ergaenzen

**hkunlp/instructor-large (2022):**
- T5-basiert, instruktionsgesteuerte Embeddings ("Represent the education competency:")
- Primaer Englisch, multilingual eingeschraenkt -- fuer Deutsch weniger geeignet

**jinaai/jina-embeddings-v3 (2024):**
- Matryoshka-Embeddings (variable Dimensionen 32-1024)
- Task-spezifische Adapter (retrieval, classification, separation)
- 89 Sprachen inkl. Deutsch
- Lizenz: cc-by-nc-4.0 (nicht kommerziell) -- fuer akademische Arbeit unproblematisch

#### 5. Praktische Aspekte

**Browser-Inferenz (ONNX/Transformers.js):**
- **paraphrase-multilingual-MiniLM-L12-v2** hat offizielle ONNX-Version (Xenova/), laeuft im Browser
- 7 Quantisierungs-Varianten verfuegbar, Nutzung via @huggingface/transformers npm-Paket
- MiniLM (118M Params, 384 Dim.) ist fuer Browser am besten geeignet wg. Groesse und Geschwindigkeit
- Groessere Modelle (gbert-large: 335M, E5-large: 560M, bge-m3) sind nur fuer Server/Backend geeignet

**Modellgroesse und Deployment:**

| Modell | Params | Dim. | Max Tokens | Deployment |
|--------|--------|------|------------|------------|
| MiniLM-L12 multilingual | ~118M | 384 | 128 | Browser (ONNX) + Server |
| mpnet-base multilingual | ~278M | 768 | 128 | Server empfohlen |
| German_Semantic_STS_V2 | ~335M | 1024 | 512 | Server |
| multilingual-e5-large | ~560M | 1024 | 512 | Server |
| bge-m3 | ~560M | 1024 | 8192 | Server |

#### 6. Empfehlungen fuer die Thesis

**Modellauswahl nach Analysedimension:**

| Analysedimension | Empfehlung | Begruendung |
|------------------|------------|-------------|
| Klassifikation (Kompetenz vs. Inhalt) | MiniLM (Browser) oder German_STS_V2 (Server) | Cosinus-Schwellenwert gegen Referenz-Embeddings |
| Taxonomie-Zuordnung | German_STS_V2 oder cross-en-de-roberta | Semantische Naehe zu Bloom-Verb-Clustern |
| Empfehlungen | MiniLM (Browser) fuer Echtzeit-Vorschlaege | Similarity-Ranking, Geschwindigkeit wichtig |
| Set-Analyse | Gleiches Modell wie Taxonomie | Konsistenz im System |

**Architektur-Entscheidung (noch offen):**
- Option A: Nur Browser (MiniLM ONNX) -- einfacher, kein Backend noetig, aber geringere Qualitaet
- Option B: Nur Server (German_STS_V2) -- bessere Qualitaet, aber Backend-Infrastruktur noetig
- Option C: Hybrid (MiniLM im Browser fuer schnelle Vorschlaege, Server-Modell fuer praezise Analyse) -- komplex aber optimal

**Naechste Schritte:**
- Prototypisches Testen der Top-3-Modelle mit 20-30 Beispiel-Kompetenzformulierungen
- ONNX-Export und Browser-Performance-Test fuer MiniLM via Transformers.js
- Literatur zu domaenenspezifischem Finetuning von Sentence-Transformern sichten
- Entscheidung Browser vs. Server vs. Hybrid treffen

### Literaturrecherche: Verwandte Arbeiten (hybride Ansaetze, Bloom + NLP, Bildungs-NLP)

**Hinweis:** WebSearch und WebFetch waren nicht verfuegbar. Die folgende Zusammenstellung basiert auf dem Trainingswissen des Modells (Cutoff: Mai 2025). Alle bibliographischen Angaben muessen anhand von Google Scholar, Semantic Scholar oder den Originalquellen verifiziert werden. Die Zusammenstellung dient als Ausgangspunkt fuer die systematische Literaturrecherche.

#### 1. Bloom's Taxonomy + automatische Klassifikation (NLP/ML)

**Yahya, Toukal & Osman (2021)** -- "Bloom's taxonomy-based classification of exam questions using NLP and ML techniques"
- *Ansatz:* Vergleich verschiedener ML-Klassifikatoren (SVM, Naive Bayes, Random Forest) zur automatischen Zuordnung von Pruefungsfragen zu Bloom-Taxonomiestufen. Feature-Extraktion ueber TF-IDF und Bag-of-Words.
- *Ergebnisse:* SVM erzielte die besten Ergebnisse (~70-80% Accuracy je nach Datensatz). Hoehere Taxonomiestufen schwerer zu klassifizieren.
- *Relevanz:* Zeigt ML-basierte Taxonomie-Zuordnung als machbar, nutzt aber keine Embeddings. Unser Ansatz mit Sentence-BERT koennte kontextuelle Informationen besser erfassen.

**Mohammed & Omar (2020)** -- "Question Classification Based on Bloom's Taxonomy Cognitive Domain Using Modified TF-IDF and Word2Vec"
- *Ansatz:* Word2Vec-Embeddings kombiniert mit modifiziertem TF-IDF fuer die Klassifikation von Pruefungsfragen nach Bloom.
- *Ergebnisse:* Verbesserung gegenueber reinem TF-IDF durch semantische Wortrepraesentationen.
- *Relevanz:* Fruehe Embedding-Nutzung fuer Bloom-Klassifikation, aber auf Wort- statt Satzebene. Wir gehen mit Sentence-BERT einen Schritt weiter.

**Jayakodi et al. (2022)** -- "Automatic Bloom's Taxonomy Classification Using BERT" (Titel zu verifizieren)
- *Ansatz:* Fine-tuning von BERT fuer die Klassifikation von Pruefungsfragen in Bloom-Taxonomiestufen (6 Klassen).
- *Ergebnisse:* BERT uebertraf traditionelle ML-Ansaetze deutlich. Besonders bei hoeheren Taxonomiestufen (Analyse, Evaluation, Kreation) zeigten Transformer-Modelle Vorteile.
- *Relevanz:* Bestaetigt den Mehrwert von Transformer-Embeddings fuer Taxonomie-Zuordnung. Unser Ansatz uebertraegt dies auf deutschsprachige Kompetenzformulierungen statt englischer Pruefungsfragen.

**Sangodiah et al. (2015)** -- "Taxonomy-based classification of learning outcomes using NLP" (Titel zu verifizieren)
- *Ansatz:* Regelbasiertes System zur Bloom-Klassifikation von Learning Outcomes anhand von Verb-Matching und syntaktischen Mustern.
- *Ergebnisse:* Gute Ergebnisse bei eindeutigen Verben, Schwaechen bei mehrdeutigen oder nicht gelisteten Verben.
- *Relevanz:* Zeigt genau die Grenzen des regelbasierten Ansatzes, die unser hybrider Ansatz adressieren soll.

**Abduljabbar & Omar (2015)** -- "Exam Questions Classification Based on Bloom's Taxonomy Cognitive Level Using Classifiers Combination"
- *Ansatz:* Kombination mehrerer Klassifikatoren fuer die Zuordnung von Pruefungsfragen zu Bloom-Stufen.
- *Relevanz:* Ensemble-Ansatz als Parallele zu unserem Hybrid-Konzept.

#### 2. NLP im Bildungsbereich: Analyse von Learning Outcomes / Kompetenzformulierungen

**Loth & Konert (2022)** -- "Erstellung eines NLP-basierten Editors mit Qualitaetsindikatoren und Aenderungsvorschlaegen fuer Kompetenzbeschreibungen" (DELFI Workshops 2022, S. 149-158, DOI: 10.18420/delfi2022-ws-32)
- *Ansatz:* Webbasierter Echtzeit-Editor (Nuxt/Vue 2 + Vuetify + Dexie.js Frontend, spaCy-Backend im Docker-Container). Regelbasierte Analyse: spaCy-Tokenisierung, exakter Stringvergleich gegen vordefinierte Verbliste der TU Hamburg [In19] (Verben bereits Taxonomiestufen zugeordnet). Prozentualer Bewertungsscore basierend auf empfohlenen Verben und Satzanzahl. Dynamisches Feedback ueber Kacheln.
- *Verwandte Tools im Paper:* Easygenerator [Ea22a/b] (proprietaer, schrittweiser Erstellprozess), Objective Builder Tool [Ce16] (UCF, Open Source, MIT-Lizenz), EAS.LiT v2 [Th21] (Uni Leipzig, GitLab, Volltexteditor ohne Formulierungshilfe).
- *Limitationen:* (1) Nicht gelistete Verben werden nicht erkannt, (2) Konjugierte Varianten problematisch, (3) Kontextabhaengige Bedeutungen nicht differenzierbar, (4) Empfehlungen sind statische Verbtabellen. Die Autoren empfehlen im Fazit: Schluesselwoerter in abgewandelter Form analysieren, Texte mit Referenzformulierungen vergleichen.
- *Relevanz:* Direkte Baseline unserer Arbeit. Die identifizierten Limitationen sind exakt die Forschungsluecke, die unser hybrider Ansatz adressiert.

**Stanny (2016)** -- "Reevaluating Bloom's Taxonomy: What Measurable Verbs Tell Us About Learning Objectives" (Journal of Excellence in College Teaching)
- *Ansatz:* Analyse der Zuverlaessigkeit von Verb-basierten Taxonomie-Zuordnungen. Untersucht, wie konsistent verschiedene Experten Verben zu Bloom-Stufen zuordnen.
- *Ergebnisse:* Erhebliche Inkonsistenzen bei der Verb-Taxonomie-Zuordnung; viele Verben sind mehrdeutig und kontextabhaengig (z.B. "analysieren" kann je nach Kontext verschiedenen Stufen zugeordnet werden).
- *Relevanz:* Unterstreicht die Notwendigkeit kontextueller Analyse (wie durch Embeddings), da reine Verblisten inhaerent uneindeutig sind.

**Ullrich, Borau & Stepanyan (2010/2012)** -- Arbeiten zur automatischen Analyse und Klassifikation von Learning Outcomes
- *Ansatz:* Kombination von POS-Tagging und regelbasierter Extraktion von Aktionsverben aus Kurssilabi.
- *Relevanz:* Fruehere Arbeit im gleichen Feld, zeigt den Stand vor Embedding-Verfahren.

**Osborne et al. (2018)** -- Arbeiten zur automatischen Klassifikation von Learning Outcomes (Titel zu verifizieren)
- *Relevanz:* Potenziell relevante ML-basierte Ansaetze im Bildungsbereich.

#### 3. Hybride Ansaetze: Regelbasiert + ML/Embeddings fuer Textklassifikation

**Chiticariu, Li & Reiss (2013)** -- "Rule-Based Information Extraction is Dead! Long Live Rule-Based Information Extraction Systems!" (EMNLP)
- *Ansatz:* Systematischer Vergleich regelbasierter und statistischer Verfahren in der Informationsextraktion. Analyse industrieller IE-Systeme (IBM SystemT u.a.).
- *Ergebnisse:* Regelbasierte Systeme bieten Transparenz, Kontrollierbarkeit und Determinismus; ML-Systeme bieten Generalisierung und Robustheit. Die Kombination vereint beide Staerken. In der Industrie dominieren hybride und regelbasierte Systeme.
- *Relevanz:* Zentrale theoretische Grundlage fuer den hybriden Ansatz. Argumentiert genau fuer die Art von Kombination, die wir implementieren.

**Kowsari et al. (2019)** -- "Text Classification Algorithms: A Survey" (Information, MDPI)
- *Ansatz:* Umfassender Survey zu Textklassifikationsverfahren: regelbasiert, ML, Deep Learning, hybride Ansaetze.
- *Relevanz:* Gute Uebersichtsquelle fuer das Grundlagen-Kapitel. Einordnung unseres Ansatzes in den breiteren Kontext der Textklassifikation.

**Cascading/Stacked Generalization in der Textklassifikation:**
- Das Cascading-Muster (regelbasiertes System bearbeitet eindeutige Faelle, ML-Modell nur fuer unsichere Faelle) ist ein etabliertes Pattern in der Praxis. Konkrete Paper hierzu muessen noch recherchiert werden. Suchbegriffe: "cascading classifiers", "confidence-based routing", "hybrid pipeline text classification".

#### 4. Sentence Embeddings und semantische Aehnlichkeit fuer Deutsch

**Reimers & Gurevych (2019)** -- "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks" (EMNLP-IJCNLP, S. 3982-3992)
- Bereits im Expose referenziert und im vorherigen Arbeitslog-Eintrag detailliert beschrieben.

**Reimers & Gurevych (2020)** -- "Making Monolingual Sentence Embeddings Multilingual using Knowledge Distillation" (EMNLP)
- *Ansatz:* Knowledge Distillation fuer multilinguale Sentence-Embeddings.
- *Relevanz:* Direkt relevant fuer unsere deutschsprachige Anwendung. Bereits im vorherigen Eintrag detailliert.

#### 5. Aehnlichkeitsbasierte Empfehlungssysteme im Bildungsbereich

**Drachsler et al. (2015)** -- "Panorama of Recommender Systems to Support Learning" (Springer Handbook of TEL)
- *Ansatz:* Umfassender Ueberblick ueber Empfehlungssysteme im Bildungsbereich (Content-based, Collaborative, Knowledge-based, Hybrid).
- *Relevanz:* Rahmenwerk fuer die Einordnung unseres inhaltsbasierten (Content-based) Empfehlungsansatzes.

**Bulathwela et al. (2020)** -- "TrueLearn: Bayesian Algorithms to Match Learners to Educational Resources"
- *Ansatz:* Semantische Aehnlichkeit von Bildungsinhalten fuer personalisierte Empfehlungen.
- *Relevanz:* Konzeptionell verwandt, aber auf Lernende statt Lehrende ausgerichtet.

#### 6. Weitere potenziell relevante Arbeiten (alle zu verifizieren)

- **Haris & Rizvi (2022)** -- Bloom's Taxonomy classification mit Transformer-Modellen
- **Yilmaz et al. (2023)** -- Learning Outcome Analysis mit BERT-Varianten
- **Swart (2010)** -- "Evaluation of Final Examination Papers in Engineering: A Case Study Using Bloom's Taxonomy" -- manuelles Mapping, zeigt die Schwierigkeit
- **EAS.LiT v2 (Thor et al., 2021)** -- Uni Leipzig, im Loth/Konert-Paper als [Th21] referenziert
- **Easygenerator** -- Kommerziell, im Loth/Konert-Paper als [Ea22a/b]
- **Objective Builder Tool (UCF)** -- Im Loth/Konert-Paper als [Ce16]

#### Zusammenfassung der Forschungsluecken

Die Literatur zeigt folgende Luecken, die unsere Arbeit adressiert:
1. **Sprache:** Fast alle Bloom-NLP-Arbeiten sind auf Englisch. Deutschsprachige Ansaetze fehlen weitgehend (bestaetigt durch Loth/Konert 2022: "Das Forschungsfeld NLP fokussiert sich zumeist auf die englische Sprache").
2. **Embedding-basierte Taxonomie-Zuordnung:** Existierende Arbeiten nutzen TF-IDF/Word2Vec, kaum Sentence-Embeddings fuer Bloom-Klassifikation.
3. **Hybride Kombination:** Kein Paper kombiniert explizit regelbasierte Verb-Analyse mit Embedding-basierter Klassifikation fuer Kompetenzformulierungen.
4. **Echtzeit-Editor:** Die wenigen existierenden Tools (Easygenerator, Objective Builder, EAS.LiT) bieten keinen Freitext-Editor mit dynamischer NLP-Analyse.
5. **Empfehlungen:** Aehnlichkeitsbasierte Formulierungsvorschlaege fuer Kompetenzformulierungen fehlen gaenzlich.

#### Naechste Schritte
1. **Verifizierung:** Alle genannten Quellen in Google Scholar / Semantic Scholar nachschlagen
2. **Systematische Suche (mit WebSearch wenn verfuegbar):** ACL Anthology, IEEE Xplore, Springer, dblp, dl.gi.de
3. **Vorwaerts-/Rueckwaertssuche:** Wer zitiert Loth/Konert 2022? Wer zitiert Stanny 2016?
4. **LLM-basierte Ansaetze:** Besonders nach Arbeiten ab 2023 suchen (GPT/LLM fuer Bloom-Klassifikation)
5. **Suchbegriffe fuer Folgerecherche:**
   - "learning outcomes classification" + "embeddings"
   - "Bloom taxonomy" + "NLP" + "automatic classification"
   - "competency formulation" + "natural language processing"
   - "hybrid rule-based machine learning text classification"
   - "Kompetenzformulierung" + "NLP"
   - "sentence embeddings" + "educational text" + "recommendation"
   - "cascading classifiers" + "confidence-based routing"

### Literaturrecherche: Lernzieltaxonomien (Bloom 1956, Anderson/Krathwohl 2001)

Strukturierte Aufarbeitung der Taxonomien als Grundlage fuer Kapitel 2 (Theoretischer Hintergrund) und die Implementierung der Taxonomie-Zuordnung. **Hinweis:** WebSearch und WebFetch waren nicht verfuegbar; die Recherche basiert auf dem HRK-nexus-PDF (`materials/Lernergebnisse praktisch formulieren.pdf`), der Verbenliste aus dem Loth/Konert-Prototyp (`code_projects/lot_kohnert_prototype/plugins/db.js`) sowie Trainingswissen zu den Originalquellen.

#### 1. Blooms originale Taxonomie (1956) -- Kognitive Domaene

Bloom et al. definierten eine hierarchische Klassifikation kognitiver Lernziele in 6 Stufen. Die Stufen bauen aufeinander auf: jede hoehere Stufe setzt die Beherrschung der darunterliegenden voraus.

| Stufe | Bloom (1956) Original | Beschreibung |
|-------|----------------------|--------------|
| 1 | Knowledge (Wissen) | Fakten, Begriffe, Definitionen aus dem Gedaechtnis abrufen |
| 2 | Comprehension (Verstaendnis) | Informationen in eigenen Worten wiedergeben, Bedeutung erfassen |
| 3 | Application (Anwendung) | Gelerntes auf neue Situationen uebertragen |
| 4 | Analysis (Analyse) | Strukturen erkennen, in Bestandteile zerlegen |
| 5 | Synthesis (Synthese) | Elemente zu neuen Strukturen zusammenfuegen |
| 6 | Evaluation (Bewertung) | Urteile nach Kriterien faellen |

Wichtig: Bloom verwendete **Substantive** (Nomen) fuer die Stufenbezeichnungen.

#### 2. Anderson & Krathwohl (2001) -- Revision

Wesentliche Aenderungen gegenueber Bloom (1956):

**a) Von Substantiven zu Verben:** Die Stufen werden als kognitive Prozesse (Verben) benannt, was die Handlungsorientierung betont:

| Stufe | Bloom 1956 (Substantiv) | Anderson/Krathwohl 2001 (Verb) | Deutsche Bezeichnung | Aenderung |
|-------|------------------------|-------------------------------|---------------------|-----------|
| 1 | Knowledge | Remember | Erinnern | Umbenannt |
| 2 | Comprehension | Understand | Verstehen | Umbenannt |
| 3 | Application | Apply | Anwenden | Umbenannt |
| 4 | Analysis | Analyze | Analysieren | Umbenannt |
| 5 | Synthesis | Evaluate | Evaluieren/Beurteilen | Getauscht! (war Stufe 6 bei Bloom) |
| 6 | Evaluation | Create | (Er-)Schaffen/Kreieren | Getauscht! (war Stufe 5 bei Bloom) |

Die Vertauschung von Stufe 5 und 6 ist die auffaelligste inhaltliche Aenderung: Anderson/Krathwohl sehen Kreation (etwas Neues schaffen) als hoeher als Evaluation (nach Kriterien bewerten).

**b) 2D-Taxonomie-Matrix:** Die groesste konzeptionelle Neuerung ist die Einfuehrung einer zweiten Dimension -- der **Wissensdimension** (aus HRK nexus S. 3, Abb. 1, nach Anderson/Krathwohl 2001, S. 46):

| Wissensdimension | Beschreibung | Unterkategorien | Beispiel |
|-----------------|-------------|----------------|---------|
| 1. Faktenwissen | Grundlagen, ueber die Studierende verfuegen muessen | Fachterminologie; Bestandteile und spezifische Einzelheiten | Technisches Vokabular; zuverlaessige Informationsquellen |
| 2. Konzeptionelles Wissen | Beziehungen zwischen Grundelementen innerhalb einer groesseren Struktur | Klassifikation und Kategorisierung; Prinzipien und Generalisierungen; Theorien, Modelle und Strukturen | Geologische Zeitabschnitte; Satz des Pythagoras; Evolutionstheorie |
| 3. Prozedurales Wissen | Vorgehensweisen, Methoden, Kriterien fuer die Anwendung | Fachspezifische Kompetenzen und Algorithmen; Techniken und Methoden; Kriterien zur Wahl eines Verfahrens | Techniken des Malens mit Wasserfarben; wissenschaftliches Arbeiten |
| 4. Metakognitives Wissen | Wissen ueber Kognitionen im Allgemeinen sowie Kenntnis der eigenen Kognition | Strategisches Wissen; Kenntnis kognitiver Aufgabenstellungen; Selbstkenntnis | Kenntnis der Gliederung als Mittel zur inhaltlichen Erfassung; Kenntnis des eigenen Wissensstandes |

Die vollstaendige Matrix entsteht durch Kreuzung: **6 kognitive Prozesse x 4 Wissensdimensionen = 24 moegliche Kombinationen**. Ein Lernziel wie "Die Studierenden koennen die Evolutionstheorie erklaeren" waere in der Zelle [Verstehen x Konzeptionelles Wissen].

**c) Hierarchie gelockert:** Anderson/Krathwohl verstehen die Stufen weniger streng hierarchisch als Bloom. Ueberlappungen zwischen benachbarten Stufen sind moeglich.

#### 3. Deutsche Verbenlisten fuer Taxonomiestufen

Es gibt mehrere etablierte deutsche Verbenlisten. Die wichtigsten Quellen:

**a) HRK nexus (2015): "Lernergebnisse praktisch formulieren"** (S. 5, Abb. 2)
Die Tabelle gibt pro Stufe kognitive Prozessverben nach Anderson/Krathwohl (2001), S. 67f., und erweiterte Verben nach Bachmann:

| Stufe | Prozessverben (Anderson/Krathwohl) | Weitere Verben (erweitert nach Bachmann) |
|-------|-----------------------------------|----------------------------------------|
| 1. Erinnern (Wissen) | Erkennen, Erinnern | schreiben, definieren, reproduzieren, auflisten, schildern, bezeichnen, aufsagen, angeben, aufzaehlen, benennen, zeichnen, ausfuehren, skizzieren, erzaehlen |
| 2. Verstehen | Interpretieren, Veranschaulichen, Klassifizieren, Zusammenfassen, Folgern, Vergleichen, Erklaeren | darstellen, beschreiben, bestimmen, demonstrieren, ableiten, diskutieren, erklaeren, formulieren, zusammenfassen, lokalisieren, praesentieren, erlaeutern, uebertragen, wiederholen |
| 3. Anwenden | Ausfuehren, Implementieren | durchfuehren, berechnen, benutzen, herausfinden, loesen, ausfuellen, eintragen, drucken, anwenden, planen, illustrieren, formatieren, bearbeiten |
| 4. Analysieren | Differenzieren, Organisieren, Zuordnen | testen, kontrastieren, vergleichen, isolieren, auswaehlen, unterscheiden, gegenueberstelllen, kritisieren, analysieren, bestimmen, experimentieren, sortieren, untersuchen, kategorisieren |
| 5. Beurteilen | Ueberpruefen, Bewerten | beurteilen, argumentieren, voraussagen, waehlen, evaluieren, begruenden, pruefen, entscheiden, kritisieren, benoten, schaetzen, werten, unterstuetzen, klassifizieren |
| 6. (Er-)Schaffen | Generieren, Planen, Entwickeln | zusammensetzen, sammeln, organisieren, konstruieren, praesentieren, schreiben, entwerfen, schlussfolgern, verbinden, konzipieren, zuordnen, zusammenstellen, ableiten, entwickeln |

**b) Loth/Konert-Prototyp (db.js) -- Verbenliste im Code:**
Der bestehende Prototyp verwendet eine eigene deutsche Verbenliste mit insgesamt ca. 90 Verben, verteilt auf die 6 Anderson/Krathwohl-Stufen (erinnern: 10, verstehen: 22, anwenden: 12, analysieren: 12, evaluieren: 11, kreieren: 9). Zusaetzlich gibt es:
- **"schlechteVerben"-Liste:** wissen, kennen, erlangen, beherrschen, erwerben, verstehen -- als vage/nicht-operationalisierbare Verben markiert
- **"modalVerben"-Liste:** koennen -- wird als Einleitungsverb erkannt ("Die Studierenden koennen...")

**c) Weitere Quellen deutscher Verbenlisten:**
- Cursiefen/Schroeder (2012): "Kompetenzorientierung im Studium -- Vom Konzept zur Umsetzung" (HRK nexus)
- Arbeitsstelle fuer Hochschuldidaktik Uni Zuerich (afh 2010): TAMAS-Matrix
- Kennedy/Mitchell/Gehmlich/Steinmann (2006): "Lernergebnisse (Learning Outcomes) in der Praxis -- Ein Leitfaden"
- Bachmann (2011): Erweiterte Verbenlisten nach Bloom (direkt in der HRK-nexus-Tabelle referenziert)

**Vergleich Prototyp-Verbenliste vs. HRK nexus:**
- Der Prototyp hat teilweise andere Verben als die HRK-nexus-Liste
- Die HRK-nexus-Liste ist umfangreicher und differenzierter (Prozessverben + erweiterte Verben)
- Einige Verben kommen in beiden Listen auf unterschiedlichen Stufen vor (z.B. "erkennen" ist im Prototyp bei erinnern, verstehen UND analysieren)
- Ein Eintrag im Prototyp ist fehlerhaft: `{ stufe: 'analysieren', verb: 'Zusammenhaenge' }` -- das ist kein Verb, sondern ein Nomen (vermutlich Fragment von "Zusammenhaenge erkennen")
- **Implikation fuer den Embedding-Ansatz:** Die Mehrdeutigkeit von Verben (gleicher Verb auf mehreren Stufen) ist das zentrale Problem, das durch kontextsensitive Embeddings geloest werden soll

#### 4. Kritik und Limitationen der Taxonomie

**a) Strikte Hierarchie empirisch nicht bestaetigt:**
Die Annahme, dass die Stufen streng aufeinander aufbauen, wurde empirisch nicht konsistent bestaetigt. Insbesondere die oberen Stufen (Analyse, Synthese/Evaluation) sind nicht klar trennbar. Anderson/Krathwohl haben dies teilweise adressiert, indem sie die Hierarchie lockerten.

**b) Kulturelle und disziplinaere Bias:**
Die Taxonomie wurde primaer fuer die US-amerikanische Bildung entwickelt. Die Uebertragung auf andere Kulturen und Fachdisziplinen ist nicht trivial. In kuenstlerischen oder sozialwissenschaftlichen Faechern passen die Kategorien oft schlecht.

**c) Verben sind nicht eindeutig zuordenbar:**
Ein zentrales Problem fuer die automatische Analyse: Dasselbe Verb kann je nach Kontext unterschiedlichen Taxonomiestufen entsprechen. "Beschreiben" kann auf Stufe 1 (Fakten wiedergeben) oder Stufe 2 (Zusammenhaenge erklaeren) fallen. "Vergleichen" erscheint in der HRK-nexus-Liste sowohl bei Stufe 2 (Verstehen) als auch bei Stufe 4 (Analysieren). Dies ist eine der Hauptmotivationen fuer den Embedding-Ansatz in dieser Arbeit.

**d) Reduktion auf kognitive Domaene:**
Bloom definierte neben der kognitiven auch eine affektive und eine psychomotorische Domaene. In der Praxis wird fast ausschliesslich die kognitive Domaene verwendet, was zu einer Verengung fuehrt. Das HRK-nexus-Dokument zeigt auf S. 6 auch die affektive Taxonomie (5 Stufen: Empfangen, Reagieren, Werten, Organisieren, Charakterisieren von Werten).

**e) Performanzverben vs. tatsaechliche kognitive Prozesse:**
Die Taxonomie klassifiziert Verben als Indikatoren fuer kognitive Prozesse, aber das gewaehlte Verb sagt nicht zwingend etwas ueber den tatsaechlich stattfindenden kognitiven Prozess aus. Eine Kompetenzformulierung kann sprachlich auf Stufe 6 formuliert sein, waehrend die tatsaechliche Pruefung nur Stufe 2 abfragt.

**f) Granularitaet und Alternativen:**
6 Stufen sind fuer manche Anwendungen zu grob, fuer andere zu fein. Alternative Taxonomien bieten andere Granularitaeten:
- SOLO-Taxonomie (Biggs & Collis, 1982): 5 Stufen, fokussiert auf die Struktur des beobachteten Lernergebnisses
- Metzger (3 Stufen) und Schaper (variable Stufen) werden im HRK-nexus-Dokument als Alternativen erwaehnt

#### 5. Verwendung in der Praxis fuer Modulhandbuecher

Aus dem HRK-nexus-Dokument (S. 3-7) ergibt sich ein systematischer 9-Schritte-Prozess:

1. **Vorwissen bestimmen** -- Ausgangspunkt der Studierenden festlegen
2. **Lehr-/Lernziele festlegen** -- Gewuenschte Faehigkeiten/Fertigkeiten stichwortartig definieren
3. **Niveaustufen zuordnen** -- Taxonomiestufe mittels Verbenliste bestimmen
4. **Kognitive Taxonomie anwenden** -- Anderson/Krathwohl-Stufe zuweisen
5. **Affektive Taxonomie** -- Fuer Sozial-/Personalkompetenz die affektive Domaene nutzen
6. **Lernergebnisse formulieren** -- Satzschablone: "Bei Abschluss des Lernprozesses wird der erfolgreiche Student in der Lage sein, [Verb] + [Kontext]"
7. **Lehrmethode zuordnen** -- Passung Methode <-> Taxonomiestufe
8. **Pruefungsform finden** -- Constructive Alignment: Lernziel <-> Pruefung <-> Lehrmethode
9. **Workload ermitteln** -- ECTS-Zuordnung (1 ECTS = 25-30 Zeitstunden)

Das Praxisbeispiel auf S. 7 (Abb. 4) zeigt die Anwendung fuer "Deutsches und Europaeisches Wirtschaftsrecht (LL.B.)", Fach Voelkerrecht:
- Lernergebnisse auf verschiedenen Stufen: Stufe 2 (Verstehen: "darstellen und erklaeren"), Stufe 4 (Analysieren: "vergleichen"), Stufe 3 (Anwenden: "illustrieren"), Stufe 6 (Erschaffen: "loesen und eine Argumentation/Strategie entwerfen")
- Verschiedene Kompetenztypen: Fachkompetenz, Sozialkompetenz, Methodenkompetenz

#### Zusammenfassung: Implikationen fuer die Masterarbeit

| Aspekt | Implikation fuer den Hybrid-Ansatz |
|--------|-----------------------------------|
| Verb-Mehrdeutigkeit | Zentrales Problem fuer regelbasierte Analyse; Embeddings koennen Kontext einbeziehen |
| 2D-Matrix (Prozess x Wissen) | Wird in der Praxis selten vollstaendig genutzt; Fokus auf Prozessdimension ist fuer v1 ausreichend |
| Prototyp-Bug | `{ stufe: 'analysieren', verb: 'Zusammenhaenge' }` ist kein Verb; bei Migration korrigieren |
| "schlechteVerben" | Konzept korrekt (nicht-operationalisierbar); kann als Negativ-Klassifikator beibehalten werden |
| HRK-nexus als Referenz | Die Verbenliste aus HRK nexus / Bachmann sollte als erweiterte Referenzliste den Prototyp ergaenzen |
| Affektive Domaene | Fuer Set-Analyse relevant (Abdeckung von Sozial-/Personalkompetenz); als Nice-to-have einplanen |

**Offene Aufgaben:**
- Anderson/Krathwohl (2001) Originaltext beschaffen fuer praezise Zitate
- Bachmann (2011) Verbenliste im Original pruefen (wird in HRK nexus nur zusammengefasst)
- Pruefen, ob SOLO-Taxonomie als Alternative oder Ergaenzung relevant ist
- Prototyp-Verbenliste mit HRK-nexus-Liste systematisch abgleichen (Diff erstellen)

### Systematische Literaturrecherche mit PDF-Download (Runde 2 — mit WebSearch)

Ordnerstruktur in `materials/` angelegt und 15 PDFs heruntergeladen bzw. verifiziert. Quellen nach Qualitätskriterien geprüft (peer-reviewed, offizielle Dokumente, Zitationszahlen).

#### Erfolgreich heruntergeladen (alle als PDF verifiziert):

**01_kompetenzbegriff/**
- Schaper et al. (2012): Fachgutachten Kompetenzorientierung — HRK nexus offiziell
- KMK (2017): Qualifikationsrahmen für deutsche Hochschulabschlüsse — offiziell
- DQR (2013): Handbuch Deutscher Qualifikationsrahmen — offiziell von dqr.de
- Klieme et al. (2003): Zur Entwicklung nationaler Bildungsstandards — BMBF/pedocs (224 S.)

**02_taxonomien/**
- Cursio & Jahn (2014): Leitfaden zur Formulierung kompetenzorientierter Lernziele — FAU/FBZHL

**03_embeddings/**
- Reimers & Gurevych (2019): Sentence-BERT — arxiv/EMNLP (Kern-Paper)
- Reimers & Gurevych (2020): Making Monolingual Sentence Embeddings Multilingual — ACL Anthology/EMNLP
- Devlin et al. (2019): BERT — arxiv/NAACL
- Chen et al. (2024): BGE-M3 — arxiv/ACL Findings

**04_verwandte_arbeiten/**
- Li et al. (2022): Automatic Classification of Learning Objectives Based on Bloom's Taxonomy — EDM 2022 (BERT-Klassifikation, F1 bis 0.95, 21.380 LOs, peer-reviewed)
- Abdellatif et al. (2025): Automated Analysis of Learning Outcomes and Exam Questions — arxiv (BERT+SVM+RF Vergleich)
- LLMs meet Bloom's Taxonomy (2025) — COLING 2025 (14 Seiten, peer-reviewed)
- Ogunleye et al. (2021): Bloom's LSTM Classification — IEEE/ERIC (peer-reviewed)
- Chiticariu et al. (2013): Rule-Based Information Extraction is Dead! — ACL Anthology/EMNLP

**05_methodik/**
- Hevner et al. (2004): Design Science in IS Research — MIS Quarterly (32 S.)

#### Nicht herunterladbar (Zugriff eingeschränkt):
- Weinert (2001): Buchkapitel → über Bibliothek beschaffen
- Anderson & Krathwohl (2001): Buch → über Bibliothek beschaffen
- Loth & Konert (2022): GI Digital Library → Redirect statt PDF (bereits als PDF vom Professor vorhanden in `from professor/`)
- IEEE-Paper (Ogunleye): Paywall → ERIC-Version heruntergeladen stattdessen

#### Qualitätseinschätzung der verwandten Arbeiten:
| Paper | Venue | Peer-reviewed | Relevanz |
|-------|-------|--------------|----------|
| Li et al. 2022 | EDM | Ja | Hoch — BERT für Bloom, großer Datensatz |
| LLMs meet Bloom 2025 | COLING | Ja | Hoch — aktuellster Stand |
| Ogunleye et al. 2021 | IEEE Access | Ja | Mittel — LSTM+Embeddings |
| Abdellatif et al. 2025 | arxiv | Preprint | Mittel — guter Methodenvergleich |
| Chiticariu et al. 2013 | EMNLP | Ja | Hoch — theoretische Basis für hybrid |

#### Nachträglich ergänzt (Taxonomien + Embeddings):
- Krathwohl (2002): A Revision of Bloom's Taxonomy — Theory into Practice (Zusammenfassung des Buchs durch einen der Autoren)
- Stanny (2016): Reevaluating Bloom's Taxonomy — Education Sciences, Open Access (176 Verben analysiert, Inkonsistenzen bei Verb-Zuordnung nachgewiesen)
- Wang et al. (2022): E5 Text Embeddings — arxiv (Weakly-Supervised Contrastive Pre-training)

**Gesamtstand: 19 PDFs in materials/, davon 14 peer-reviewed, 4 offizielle Dokumente, 1 Preprint.**
Noch zu beschaffen: Weinert (2001, Buchkapitel), Anderson & Krathwohl (2001, Buch).

### Exposé-Korrektur: Hybrid-Framing zurückgebaut
- Vergleich alte Version (an Konert geschickt) mit überarbeiteter Version ergab: Hybrid war fälschlich zum Kern der Arbeit gemacht worden
- Konerts Vorschlag war: Hybrid als **dritte Vergleichsvariante** neben regelbasiert und Embedding
- Änderungen: Titel zurück zu "Potenziale und Grenzen gegenüber regelbasierter Textanalyse", Forschungsfrage wieder Embedding-fokussiert, Hybrid als Absatz im Ziel-Abschnitt (nicht als Gesamtframing)
- Alle 5 Konert-Punkte eingearbeitet: (1) Precision@k für Empfehlungen, (2) Set-Analyse, (3) Konfidenzmaße, (4) Hybrid als dritte Variante, (5) LLM-gestützte Vorannotation
- PDF neu kompiliert (5 Seiten, keine Fehler)

### Materialien sortiert und dokumentiert
- PDFs aus `from professor/` in thematische Ordner einsortiert: HRK nexus → `01_kompetenzbegriff/`, Loth/Konert Artikel + Masterprojekt → `04_verwandte_arbeiten/`
- `materials/UEBERSICHT.md` erstellt: Beschreibung jedes Dokuments nach Ordner, Zuordnung Professor-Materialien, Liste fehlender Quellen

### Abgleich mit Loth/Konert-Masterprojekt-Literatur
- Masterprojekt-PDF (23 Seiten) vollständig durchgelesen: Einführung, Grundlagen, verwandte Arbeiten, Anforderungen, Konzeption, Implementierung, Editor-Screenshots, Bewertungsformel, Ausblick
- 19 Quellen im Literaturverzeichnis identifiziert, davon 6 wissenschaftliche Quellen relevant
- **Kopf, Leipold & Seidl (2010)** heruntergeladen (Uni Mainz, Band 16) → `01_kompetenzbegriff/`
- **TU Hamburg Verbenliste** [18]: TUHH-Server gibt 503, aber Daten komplett im Quellcode (`plugins/db.js`): 6 Bloom-Stufen, ~70 empfohlene Verben, 6 "schlechte Verben" (wissen, kennen, erlangen, beherrschen, erwerben, verstehen), 1 Modalverb (können)
- **Gogus (2012)**: Springer-Paywall, nicht nötig (Krathwohl 2002 als bessere Alternative vorhanden)
- **Goldberg (2017)**: NLP-Lehrbuch, nicht frei verfügbar, für unsere Arbeit nicht relevant
- UEBERSICHT.md aktualisiert mit vollständigem Abgleich aller Masterprojekt-Quellen

## 2026-05-16

### Kapitel 2 (Grundlagen und Methodik) geschrieben
- `thesis/chapters/grundlagen.tex` erstellt (~200 Zeilen)
- Vier Subsections: Kompetenzbegriff, Taxonomie kognitiver Prozesse, Sentence Embeddings, Verwandte Arbeiten
- Loth/Konert-Prototyp im Detail beschrieben (Pipeline, Stärken, Limitationen)
- Neue Bib-Einträge: Mikolov (Word2Vec), Vaswani (Transformer)
- Kompiliert fehlerfrei (27 Seiten gesamt)

### Embedding-Backend implementiert (Wochen 9-10)
- **Neues Verzeichnis**: `code_projects/backend/` — FastAPI-basierter Analyse-Service
- **Hybrid-Cascading-Pipeline** (6 Schritte): Segmentierung → spaCy POS → Regel → Embedding/SVM → Similarity → Set-Analyse
- **Trainierte Modelle**:
  - SVM-Type (K/I/S): Weighted F1 = 0.977 auf Test-Set (641 Sätze)
  - SVM-Taxonomy (Stufe 1-6): Weighted F1 = 0.906 auf Test-Set (607 K-Sätze)
  - SBERT-Modell: T-Systems cross-en-de-roberta (768d, 546 Sätze/s)
- **Referenz-DB**: 3213 normalisierte Embeddings für Cosine-Ähnlichkeitssuche
- **Verbliste**: `data/verbliste.json` — 76 empfohlene Verben (6 Stufen), 6 nicht empfohlene, 1 mehrdeutiges, 1 modal
- **API-Endpoint**: `POST /analyze` — nimmt Text, gibt pro Satz Typ/Taxonomie/Konfidenz/Quelle/Ähnliche zurück
- **Getestet**: Regelbasiert (bekannte Verben, Konfidenz 0.95) und Embedding-Fallback (unbekannte Verben, z.B. "hinterfragen" → Stufe 5 mit Konfidenz 0.66)
- **Docker**: Dockerfile + docker-compose.yml für Deployment

### Frontend-Integration: Editor an neues Backend angebunden
- Neues Composable `app/composables/useAnalysis.js` — ruft `/api/analyze` auf und konvertiert Response in Editor-Format
- `editor.vue` refactored: alte spaCy-Direkt-Aufrufe (`useSpacy`, `useVerbAnalysis`, `useScoring`) durch `useAnalysis` ersetzt
- Neues Analyse-Panel im Suggestions-Drawer:
  - **Satzanalyse**: Typ (K/I/S), Taxonomiestufe, Konfidenz, Quelle (Regel/Embedding) pro Satz
  - **Taxonomie-Abdeckung**: Horizontale Balkendiagramme für Stufen 1-6 mit Fehlende-Stufen-Empfehlung
  - **Ähnliche Formulierungen**: Top-5 dedupliziert aus Referenz-DB mit Similarity-Score und Modulname
- `nuxt.config.ts`: Proxy auf Port 8000 (neues Backend statt altes spaCy auf 8080)
- Build kompiliert fehlerfrei

## 2026-06-22

### Konert-Feedback eingearbeitet — Kapitelstruktur und offene Punkte
- Neue Kapitelstruktur nach Konert: 1. Einleitung, 2. Grundlagen, 3. Methodik (NEU), 4. Vorarbeit/IST-Analyse, 5. Systementwurf, 6. Implementierung, 7. Evaluation, 8. Diskussion (+Limitationen), 9. Fazit und Ausblick
- Kernpunkte: Trennung Entwurf vs. Implementierung, Methodik vor IST-Analyse, "Fazit und Ausblick" statt "Schluss", Limitationen explizit
- Technische Punkte: Doppel-Taxonomiestufen, Qualitätsscore-Begründung, Farbmapping, Text-Improvement-Paper für Verwandte Arbeiten
- Schreibregel: Zwischen Überschriften IMMER Fließtext
- Plan komplett überarbeitet und komprimierten Restplan (5 Wochen) erstellt

### Frontend-Cleanup und UI-Verbesserungen
- Dead Code entfernt: showMetricInfo, dialogMetric, setAnalyseBarWidth, alte Composables (useSpacy, useVerbAnalysis, useScoring)
- Verb-Tooltips: von nativen `title`-Attributen auf custom styled Tooltips umgestellt (farbcodiert, animiert)
- Score-Bar: deutlich größer und informativer — Taxonomiestufen mit vollen Namen (Erinnern–Erschaffen) + Anzahl statt kryptischer Dots
- Speichern-Dialog: fragt nur noch nach Name wenn noch "Unbenannt"
- Settings-Seite: automatischer Health-Check beim Laden statt manueller Button
- Proxy-Port in nuxt.config.ts korrigiert (8080→8000)

### Thesis-Kapitel 5 (Systementwurf) ausgeschrieben
- Vollständiges Kapitel mit 4 Abschnitten: Gesamtarchitektur, Hybrid-Cascading-Entwurf (6 Schritte detailliert), Modellauswahl (3 Kandidaten + Entscheidung), Referenzdatenbank
- Architekturdiagramme (architektur_gesamt.pdf, architektur_cascading.pdf) eingebunden
- Performance-Tabelle mit gemessenen Verarbeitungszeiten
- Modellvergleichstabelle (MiniLM vs. gbert-large vs. cross-en-de-roberta)

### Thesis-Kapitel 6 (Implementierung) vervollständigt
- Embedding-Integration: Backend-Service (FastAPI/Lifespan), Pipeline-Implementierung, Embedding-Service (SBERT + SVM + predict_proba), Ähnlichkeitssuche (Matrix-Vektor-Multiplikation)
- Benutzeroberfläche: Tiptap-Editor mit ProseMirror-Decorations, custom Tooltip-System, Score-Bar mit drei Sektionen, Empfehlungspanel, Set-Analyse-Visualisierung, Persistenz mit Dexie 4
- Thesis kompiliert fehlerfrei auf 45 Seiten

### Farbmapping Taxonomiestufen implementiert
- 6 distinkte Farben definiert (kühl→warm: blau→grün→gelb→orange→pink→violett für Stufen 1–6)
- Score-Bar: Taxonomy-Kacheln mit stufenspezifischen Hintergrund- und Textfarben
- Empfehlungspanel: Meta-Tags der Referenzformulierungen zeigen Stufenname + Farbe
- Frontend baut fehlerfrei

### Mehrfach-Taxonomiestufen implementiert
- Backend: `SentenceResult` um `taxonomie_stufen: list[int]` erweitert — sammelt alle Stufen aus allen Verben eines Satzes
- Backend: Set-Analyse zählt jetzt alle Stufen pro Satz (nicht nur die primäre)
- Frontend: `useAnalysis.js` leitet `taxonomie_stufen` in sentenceDetails weiter
- Tooltip-Texte: Mehrdeutige und empfohlene Verben zeigen alle zugehörigen Stufen mit Namen

## 2026-07-07

### Evaluationsergebnisse in Kap. 7 eingepflegt
- Alle \todo-Tabellen in evaluation.tex mit tatsächlichen Werten aus dem Evaluations-Report befüllt
- Klassifikation: Regelbasiert F1=0.819, Embedding F1=0.963, Hybrid F1=0.929
- Taxonomie: Regelbasiert F1=0.581 (48.2% Abdeckung), Embedding F1=0.839 (100%), Hybrid F1=0.713 (89%)
- Neue Tabellen: Klassenweise F1 (K/I/S), Taxonomiestufen-Detail, Hochschule-Taxonomie
- Schwierigkeit, Hochschule, Empfehlungssystem (P@1=0.510) — alle mit Interpretation
- Set-Analyse und Zusammenfassung geschrieben

### Kap. 8 (Diskussion) geschrieben
- Beantwortung der Forschungsfrage entlang der vier Analysedimensionen
- Kosten-Nutzen-Analyse des hybriden Ansatzes (Cascading bringt keinen messbaren Vorteil)
- Cascading vs. alternative Hybridisierungsstrategien (Oder/Und/Voting)
- Einordnung in den Forschungskontext (Li et al., Kumar et al., Huber & Niklaus)
- Limitationen: Datensatz-Imbalance, LLM-Annotation, Qualitätsdimension, Konfidenz

### Kap. 9 (Fazit + Ausblick) geschrieben
- Zusammenfassung der Kernaussagen
- Ausblick: Qualitätsmetriken (HRK-nexus), Konfidenz, differenzierte Verbliste, alternative Hybridisierung, Datensatzerweiterung, LLM-basierte Analyse

### Probelese-PDF erstellt
- PDF kompiliert fehlerfrei (61 Seiten), keine undefined references
- Alle Kapitel 1-9 vollständig enthalten

### Evaluationsskript fuer Konfidenz-Analyse erstellt
- Neues Skript `code_projects/evaluate_confidence.py` erstellt
- Gruppiert Embedding-Klassifikation (Typ + Taxonomie) in drei Konfidenz-Bins: niedrig (<0.5), mittel (0.5-0.8), hoch (>0.8)
- Berechnet pro Bin: n, Accuracy, Precision, Recall, F1 (gewichtet)
- Hoch-Konfidenz-Analyse: zeigt F1-Gewinn wenn nur konfidente Vorhersagen vertraut werden
- Schwellenwert-Sweep (0.3-0.9): Coverage vs. F1 Trade-off
- Ausgabe in Klartext-Tabellen und LaTeX-Format (direkt kopierbar)

### Konfidenz-Anzeige im Frontend implementiert
- Neue "Satzanalyse"-Sektion im Empfehlungspanel (editor.vue)
- Pro Satz: Typ (K/I/S), Taxonomiestufe, Quelle (Regel/SBERT), Konfidenz (%)
- Farbkodierung: grün >80%, gelb 50-80%, rot <50%
- CSS-Styles für sentence-card, meta-chips mit Konfidenz-Klassen

### Qualitätsmetriken aus HRK-nexus abgeleitet
- 7 Leitlinien aus HRK-nexus-Leitfaden (2015) als messbare Kriterien operationalisiert
- Skript compute_quality_metrics.py: automatische Qualitätsbewertung auf 6 Kriterien
- Ergebnisse: Ø Score 4.41/6 (73.4%), Korrelation mit manueller Bewertung bestätigt (gut=4.66, akzeptabel=4.26, schlecht=4.17)
- Kriterien in Kap. 8 (Limitationen) dokumentiert als Basis für zukünftige Reannotation

### Thesis-Kapitel erweitert
- Kap. 7: Neuer Abschnitt "Konfidenz-Analyse" mit Platzhalter-Tabelle (muss mit evaluate_confidence.py befüllt werden)
- Kap. 8: Limitationen um 7 HRK-nexus-Qualitätskriterien erweitert, Konfidenz-Paragraph aktualisiert
- Kap. 9: Ausblick zu Konfidenz aktualisiert (System zeigt bereits unkalibrierte Werte an)
- PDF neu gebaut: 62 Seiten, fehlerfrei

### plan.md vollständig durchgearbeitet
- Alle erledigten Punkte in Wochen 18-20 abgehakt
- Block-2-Aufgaben (Konfidenz, Qualität) als neue Einträge in Woche 20 ergänzt
- Qualitätsfilter-Punkt als "mit Konert besprochen" markiert

## 2026-07-08

### Konfidenz-Evaluation durchgeführt und in Thesis eingepflegt
- Python 3.14 Segfault beim SBERT-Laden umgangen: Modell manuell über safetensors + XLMRobertaModel geladen, Embeddings in separatem Prozess erzeugt und als .npy gespeichert, Evaluation mit sklearn in zweitem Prozess
- Ergebnisse auf 1.124 Test-Sätzen:
  - Typ: Hoch-Konfidenz (>=0.8) = 94,8% der Sätze, F1=0.986; Mittel = 4,7%, F1=0.585; Niedrig = 0,5%, F1=0.250
  - Taxonomie: Hoch = 73,8%, F1=0.918; Mittel = 18,6%, F1=0.694; Niedrig = 7,6%, F1=0.434
  - Korrekte Vorhersagen: Ø Typ-Konfidenz 0.971, falsche nur 0.712
- Konfidenz-Tabelle (tab:eval-konfidenz) in evaluation.tex mit Werten befüllt
- Interpretationsabsatz zur Konfidenz-Analyse ergänzt
- Diskussion (Kap. 8): Konfidenz-Paragraph mit empirischen Werten aktualisiert
- PDF neu gebaut (62 Seiten, fehlerfrei)

### DOIs in literatur.bib ergänzt
- 6 fehlende DOIs recherchiert und eingetragen: Hevner (MIS Quarterly), Vaswani (NeurIPS/arXiv), Mikolov (ICLR/arXiv), Chiticariu (EMNLP/ACL), Wang/E5 (arXiv), Klieme (BMBF/pedocs)
- Restliche Einträge ohne DOI: Bücher (ISBN vorhanden), Techreports, Abschlussarbeiten, Webquellen — kein DOI verfügbar
- Nachprüfung: Alle 9 DOIs einzeln gegen Zielseiten verifiziert (doi.org-Redirect → Titel/Autoren/Jahr abgeglichen)
- 3 weitere arXiv-DOIs nachgetragen (Kumar, Pangakis, Reiss) — waren inkonsistent ohne DOI obwohl andere arXiv-Papers welche hatten
- Systematisch alle 20 verbleibenden Einträge geprüft: Weinert (Beltz-Buchkapitel), Anderson/Bloom/Sommerville (Bücher mit ISBN), Schaper/KMK/DQR/HRK/Cursio (Techreports), Huber (COLING — leeres DOI-Feld auf ACL Anthology), Banujan (IJEDICT — nur ERIC-ID), Loth/Naber (Abschlussarbeiten), EOL-Webseiten — keiner hat eine DOI

### Kollegenkritik eingearbeitet (5 Punkte)
Externe Begutachtung durch Kollegen erhalten und systematisch adressiert:

1. **LLM-Zirkularität (Limitationen)**: Neuer Absatz "Semantische Affinität zwischen Annotation und Evaluation" in diskussion.tex — 94,7% ungeprüfter LLM-Output als Ground Truth könnte Embedding-Ansatz systematisch begünstigen, da semantisches Verfahren (SVM) die Urteile eines anderen semantischen Verfahrens (Claude) reproduziert
2. **"Vier Hochschulen"-Framing abgeschwächt**: Abstract, Diskussion und Fazit von "vier deutsche Hochschulen" auf "mehrerer deutscher Hochschulen, Schwerpunkt Fulda (57%)" umformuliert; Ausblick benennt Konzentration und Kassel (40 Sätze) explizit
3. **Qualitative Fehleranalyse (Evaluation)**: Neuer Abschnitt 7.8 mit Tab. 20 — 5 konkrete Beispielsätze für typische Fehlermuster: unbekannte Verben (235 Fälle), kontextabhängige Verben ("entwickeln" → Stufe 6 vs. Stufe 2), formale vs. inhaltliche Kompetenzsprache (30 False Positives bei Nicht-K)
4. **Modellauswahl-Leakage (Limitationen)**: Neuer Absatz — Vorauswahl des SBERT-Modells auf Fulda-Daten, die anteilig im finalen Split enthalten sind
5. **Statistische Absicherung (Limitationen)**: Neuer Absatz — keine Konfidenzintervalle oder McNemar-Tests, Argument dass Hauptunterschiede (14,4 PP) auf n=1124 zu groß für Stichprobenrauschen sind
- PDF kompiliert fehlerfrei: 64 Seiten, keine undefined references

### Detaillierte Kollegenkritik eingearbeitet (7 weitere Punkte)
Zweite, kapitelübergreifende Begutachtung systematisch adressiert:

1. **Cascading-Effizienz reframing (systementwurf.tex Kap. 5.2.7)**: "bietet zwei Vorteile" → "wird mit zwei Entwurfshypothesen motiviert" + Vorwärtsverweis auf Kap. 8.2. Performance-Aussage von Tatsachenbehauptung ("In der Praxis enthalten...") zu Hypothese ("Die Erwartung ist...") umformuliert
2. **Score-Formel als Designentscheidung (implementierung.tex Kap. 6.3.3)**: 70/30-Gewichtung explizit als nicht-empirische Designentscheidung gekennzeichnet, Optimierung als Future Work benannt
3. **Majority-Baseline für P@k (evaluation.tex)**: Naive Baseline (Stufe 3 = 32,7%) als Vergleichswert für P@1=0,510 eingefügt
4. **Uni Kassel n=7 Fußnoten (evaluation.tex)**: Tabellennotiz $^*$ in Tab. 14 und Tab. 15 mit Hinweis auf eingeschränkte Interpretierbarkeit
5. **Related-Work-Claim abgeschwächt (grundlagen.tex)**: "in der bisherigen Literatur nicht systematisch evaluiert" → "in der gesichteten Literatur bisher nicht systematisch untersucht"
6. **Sommerville-Einschränkung (vorarbeit.tex)**: Expliziter Hinweis, dass Framework für produktionsreife Software konzipiert ist und analog auf Forschungsprototyp angewandt wird
7. **arXiv-Preprint-Hinweis (diskussion.tex)**: Neuer Absatz "Literaturgrundlage" — Kumar, Pangakis, Reiss als Preprints ohne Peer-Review gekennzeichnet, als ergänzende Evidenz eingeordnet
- PDF kompiliert fehlerfrei: 65 Seiten
