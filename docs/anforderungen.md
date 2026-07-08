# Anforderungserhebung — Hybrider Kompetenzformulierungs-Editor

Abgeleitet aus: Prototyp-Analyse (S1–S8), Konert-Feedback (5 Punkte), Literaturrecherche, HRK-nexus-Qualitätskriterien.

Letzte Aktualisierung: 2026-04-07

---

## Anforderungsquellen

| Quelle | Herkunft | Beitrag |
|--------|----------|---------|
| S1–S8 | Prototyp-Schwächen (results.md §5.8) | Funktionale Lücken des bestehenden Systems |
| K1–K5 | Konert-Feedback (results.md §7) | Betreuer-Anforderungen an Evaluation und Features |
| L-Taxo | Krathwohl (2002), Stanny (2016), Cursio (2013) | Zweidimensionalität, Verb-Überlappung → Kontextanalyse nötig |
| L-Embed | Reimers (2019/2020), Kumar (2025) | Technische Möglichkeiten und Grenzen von Embeddings |
| L-Hybrid | Chiticariu (2013) | Regelbasiert für Transparenz, ML für Generalisierung |
| L-Praxis | HRK nexus (2015), Kopf et al. (2010) | Qualitätskriterien für Kompetenzformulierungen |
| P-Stärken | Prototyp-Stärken (results.md §5.7) | Bewährte UI-Patterns, die erhalten bleiben sollen |

---

## Funktionale Anforderungen

### FA1: Klassifikation (Kompetenz vs. Inhaltsbeschreibung)

**Beschreibung:** Das System soll automatisch erkennen, ob ein Satz eine Kompetenzformulierung oder eine reine Inhaltsbeschreibung ist.

**Herkunft:** S4 (keine Klassifikation im Prototyp), HRK nexus S. 6 (Unterscheidung Lernziel vs. Lernergebnis), Arbeitsdefinition §1.3.

**Akzeptanzkriterien:**
- Binäre Klassifikation jedes Satzes (Kompetenz/Nicht-Kompetenz)
- Konfidenzwert für die Klassifikation (K3)
- Visuelle Kennzeichnung im Editor

**Ansatz:** Hybrid — regelbasiert wenn Verb aus Positivliste → direkt als Kompetenz; Embedding-basiert für Grenzfälle (Satz-Ähnlichkeit zu Referenzformulierungen).

### FA2: Taxonomie-Zuordnung nach Anderson/Krathwohl

**Beschreibung:** Jede erkannte Kompetenzformulierung soll einer der 6 kognitiven Prozessstufen zugeordnet werden.

**Herkunft:** S1 (exakter Stringvergleich), S2 (geschlossene Verbliste), S3 (keine Kontextsensitivität), Krathwohl 2002 (Zweidimensionalität), Stanny 2016 (Verb-Überlappung auf bis zu 6 Stufen).

**Akzeptanzkriterien:**
- Zuordnung zu einer der 6 Stufen (Erinnern–Kreieren)
- Auch für Verben, die nicht in der statischen Liste stehen (S2)
- Berücksichtigung des Satzkontexts, nicht nur des Verbs (Stanny: „select" auf allen 6 Stufen)
- Konfidenzwert für die Zuordnung (K3)

**Ansatz:** Hybrid — regelbasiert wenn Verb eindeutig einer Stufe zuordenbar (z.B. „nennen" → Erinnern); Embedding-basiert wenn Verb mehrdeutig oder nicht in Liste (Cosine-Similarity zu Referenzformulierungen pro Stufe).

### FA3: Ähnlichkeitsbasierte Empfehlungen

**Beschreibung:** Für Sätze mit niedrigem Qualitätsscore oder vagen Verben soll das System ähnliche, gut bewertete Referenzformulierungen vorschlagen.

**Herkunft:** S5 (statische Empfehlungen), K1 (Precision@k für Evaluation), Loth Future Work (NLP-basierte Domänenextraktion und Datenbankvergleich).

**Akzeptanzkriterien:**
- Top-k ähnlichste Referenzformulierungen anzeigen (k konfigurierbar, z.B. 3–5)
- Sortiert nach Cosine-Similarity
- Referenzdatenbank aus Gold-Standard und/oder FBAI-Modulhandbüchern
- Evaluation via Precision@k (K1)

**Ansatz:** Embedding — Satz-Embedding des Eingabesatzes → Nearest-Neighbor-Suche in vorberechneter Referenz-Embedding-Datenbank.

### FA4: Set-Analyse (Taxonomieabdeckung auf Modulebene)

**Beschreibung:** Überblick über die Verteilung der Taxonomiestufen aller Kompetenzformulierungen eines Moduls.

**Herkunft:** S6 (keine Set-Analyse), K2 (Set-Analyse als 4. Analyseebene).

**Akzeptanzkriterien:**
- Visualisierung der Taxonomie-Verteilung (z.B. Balkendiagramm/Radar-Chart)
- Warnung bei fehlenden Stufen oder extremer Konzentration
- Aggregation über alle Sätze eines Modultexts

**Ansatz:** Aggregation der FA2-Ergebnisse.

### FA5: Echtzeit-Analyse mit visuellem Feedback

**Beschreibung:** Der Editor soll wie im bestehenden Prototyp Near-Realtime-Feedback geben, mit farbiger Hervorhebung im Text.

**Herkunft:** P-Stärken (Sofortiges Feedback, Farbcodierung), HRK nexus S. 6 (Qualitätskriterien als Basis).

**Akzeptanzkriterien:**
- Analyse-Update nach Tipp-Pause (≤ 2 Sekunden)
- Farbcodierung: empfohlene Verben (grün), nicht empfohlene (rot), Modalverben (blau), neutrale (grau)
- Zusätzlich: Konfidenz-Indikator (z.B. Farbintensität oder Unterstreichungsstil) (K3)

### FA6: Persistenz und Verwaltung

**Beschreibung:** Kompetenzbeschreibungen können gespeichert, geladen und gelöscht werden.

**Herkunft:** P-Stärken (Dexie/IndexedDB), Prototyp-Bug (kein Update, nur add).

**Akzeptanzkriterien:**
- Speichern, Laden, Aktualisieren und Löschen von Texten
- Offline-fähig (IndexedDB)

---

## Nicht-funktionale Anforderungen

### NFA1: Konfidenzmaße und Unsicherheitsvisualisierung

**Beschreibung:** Alle automatischen Zuordnungen (Klassifikation, Taxonomie) sollen mit einem Konfidenzwert versehen werden.

**Herkunft:** K3 (Konfidenzmaße), S7 (Score zu simpel), S8 (kein Konfidenzmaß).

**Akzeptanzkriterien:**
- Cosine-Similarity als kontinuierlicher Konfidenzwert (0.0–1.0)
- Visuelle Darstellung der Unsicherheit (z.B. Farbgradient, Warnsymbol bei niedrigem Score)
- Schwellenwert konfigurierbar für Hybrid-Cascading (ab welcher Konfidenz wird Embedding-Ergebnis verwendet?)

### NFA2: Transparenz und Nachvollziehbarkeit

**Beschreibung:** Nutzer sollen verstehen können, warum das System eine bestimmte Zuordnung trifft.

**Herkunft:** Chiticariu 2013 (Transparenz als Hauptvorteil regelbasierter Systeme), Hevner G7 (Communication).

**Akzeptanzkriterien:**
- Bei regelbasierter Zuordnung: Anzeige des gematchten Verbs + Taxonomiestufe
- Bei Embedding-basierter Zuordnung: Anzeige der ähnlichsten Referenzformulierungen + Similarity-Score
- Info-Popups wie im bestehenden Prototyp (P-Stärken)

### NFA3: Deutsche Sprache

**Beschreibung:** Alle Analysen müssen für deutschsprachige Kompetenzformulierungen funktionieren.

**Herkunft:** Forschungslücke (alle Bloom-NLP-Arbeiten auf Englisch), FBAI-Modulhandbücher sind Deutsch.

**Akzeptanzkriterien:**
- Deutsches Embedding-Modell (z.B. German_Semantic_STS_V2 oder paraphrase-multilingual-MiniLM)
- Deutsche Verblisten (TU Hamburg + HRK nexus als Basis)
- Korrekte Behandlung deutscher Morphologie (Konjugation, Komposita)

### NFA4: Technologie-Migration

**Beschreibung:** Der Prototyp soll auf einen aktuellen Technologie-Stack migriert werden.

**Herkunft:** Prototyp-Probleme (Nuxt 2 → 3 Inkompatibilität, Vuetify 2 EOL).

**Akzeptanzkriterien:**
- Nuxt 4 (oder 3) mit Vue 3 Composition API
- Vuetify 3 oder alternatives UI-Framework
- Robusterer Rich-Text-Editor (z.B. Tiptap/ProseMirror statt ContentEditable-Hack)

### NFA5: Performance

**Beschreibung:** Die Analyse soll für den Nutzer flüssig und responsiv sein.

**Herkunft:** SBERT: 2042 Sätze/Sekunde auf GPU; Browser-Deployment erfordert Optimierung.

**Akzeptanzkriterien:**
- Analyse-Latenz ≤ 2 Sekunden nach Tipp-Pause
- Embedding-Berechnung entweder serverseitig (schnell) oder via ONNX im Browser (offline-fähig)

---

## Priorisierung (MoSCoW)

### Must-have (Kern der Thesis)

| ID | Anforderung | Begründung |
|----|------------|------------|
| **FA1** | Klassifikation (Kompetenz vs. Inhalt) | 1. Analysedimension der Thesis |
| **FA2** | Taxonomie-Zuordnung | 2. Analysedimension, Kern des Vergleichsexperiments |
| **FA5** | Echtzeit-Analyse + visuelles Feedback | Grundfunktionalität des Editors |
| **NFA1** | Konfidenzmaße | Konert-Anforderung K3, ermöglicht Hybrid-Cascading |
| **NFA3** | Deutsche Sprache | Forschungslücke, Alleinstellungsmerkmal |

### Should-have (wichtig für Vollständigkeit)

| ID | Anforderung | Begründung |
|----|------------|------------|
| **FA3** | Ähnlichkeitsbasierte Empfehlungen | 3. Analysedimension, Konert K1 (Precision@k) |
| **FA4** | Set-Analyse | 4. Analysedimension, Konert K2 |
| **NFA2** | Transparenz/Nachvollziehbarkeit | Chiticariu-Argument, Nutzerakzeptanz |
| **NFA4** | Technologie-Migration (Nuxt 4) | Notwendig für nachhaltige Weiterentwicklung |

### Could-have (wünschenswert)

| ID | Anforderung | Begründung |
|----|------------|------------|
| **FA6** | Persistenz + Verwaltung | Bereits im Prototyp vorhanden, Neuimplementierung nötig |
| **NFA5** | Performance ≤ 2s | Wichtig für UX, aber Server-Backend als Fallback akzeptabel |

### Won't-have (explizit ausgeschlossen)

| Thema | Begründung |
|-------|------------|
| Automatische Textgenerierung | Nicht im Forschungsumfang; LLM-basierte Generierung ist anderes Thema |
| Multilinguale Unterstützung (EN, etc.) | Fokus auf Deutsch; Erweiterbarkeit durch Modellwahl gewährleistet |
| Affektive Taxonomie (Krathwohl/Bloom) | Nur kognitive Dimension; affektive erfordert eigene Verblisten + Forschung |
| Nutzerstudie / qualitative Evaluation | Quantitative Evaluation via Gold-Standard ist Kern; Nutzerstudie wäre Folgearbeit |

---

## Mapping: Anforderungen ↔ Quellen

| Anforderung | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | K1 | K2 | K3 | K4 | K5 | Lit. |
|-------------|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| FA1 Klassifikation | | | | ✅ | | | | | | | | ✅ | | HRK |
| FA2 Taxonomie | ✅ | ✅ | ✅ | | | | | | | | | ✅ | | Krathwohl, Stanny |
| FA3 Empfehlungen | | | | | ✅ | | | | ✅ | | | | | Loth FW |
| FA4 Set-Analyse | | | | | | ✅ | | | | ✅ | | | | |
| FA5 Echtzeit | | | | | | | | | | | | | | P-Stärken |
| NFA1 Konfidenz | | | | | | | ✅ | ✅ | | | ✅ | | | |
| NFA2 Transparenz | | | | | | | | | | | | | | Chiticariu |
| NFA3 Deutsch | | | | | | | | | | | | | | Forschungslücke |

---

## Hybrid-Cascading-Logik (Entwurf)

```
Eingabe: Satz S
┌─────────────────────────────────────────────┐
│ Schritt 1: spaCy-Tokenisierung              │
│   → Verben extrahieren (POS-Tag V*)         │
│   → Satzsegmentierung                       │
└─────────┬───────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────┐
│ Schritt 2: Regelbasierter Check              │
│   Verb in Positivliste?                      │
│   ├─ JA, eindeutig (1 Stufe): → Stufe + ✅  │
│   ├─ JA, mehrdeutig (>1 Stufe): → weiter    │
│   └─ NEIN: → weiter                         │
│   Verb in Negativliste? → Warnung            │
└─────────┬───────────────────────────────────┘
          │ (mehrdeutig oder unbekannt)
┌─────────▼───────────────────────────────────┐
│ Schritt 3: Embedding-basierte Analyse        │
│   Satz-Embedding berechnen (SBERT)           │
│   Cosine-Similarity zu Referenz-Embeddings   │
│   pro Taxonomiestufe                         │
│   → Stufe mit höchster Similarity            │
│   → Konfidenzwert = max(Similarity)          │
└─────────┬───────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────┐
│ Schritt 4: Klassifikation                    │
│   Ist max(Similarity) > Schwellenwert?       │
│   ├─ JA: Kompetenzformulierung               │
│   └─ NEIN: Inhaltsbeschreibung               │
└─────────────────────────────────────────────┘
```

Dieses Cascading realisiert Konerts Hybrid-Anforderung (K4): Regelbasiert für eindeutige Fälle (schnell, transparent), Embedding für unsichere Fälle (robust, kontextsensitiv).
