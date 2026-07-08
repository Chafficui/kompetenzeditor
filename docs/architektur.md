# Architekturentwurf — Hybrider Kompetenzformulierungs-Editor

## Datum
2026-04-25

## Überblick

Das System besteht aus zwei Komponenten:

1. **Frontend** (Nuxt 4 / Vue 3): Editor-UI mit Echtzeit-Feedback
2. **Backend** (Python / FastAPI): Embedding-Berechnung, SVM-Klassifikation, Ähnlichkeitssuche

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Nuxt 4)                     │
│                                                         │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐ │
│  │ Tiptap   │  │ Analyse-     │  │ Set-Analyse-      │ │
│  │ Editor   │  │ Panel        │  │ Übersicht         │ │
│  │          │  │ • Typ K/I/S  │  │ • Taxonomie-Radar │ │
│  │ Verb-    │  │ • Stufe 1–6  │  │ • Abdeckung       │ │
│  │ Highlight│  │ • Konfidenz  │  │ • Empfehlungen    │ │
│  │          │  │ • Quelle     │  │                   │ │
│  └────┬─────┘  └──────────────┘  └───────────────────┘ │
│       │ Debounce 500ms                                  │
└───────┼─────────────────────────────────────────────────┘
        │ REST API (JSON)
┌───────▼─────────────────────────────────────────────────┐
│                  Backend (FastAPI)                        │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │              POST /api/analyze                      │  │
│  │  Input: { text: "Die Studierenden können..." }     │  │
│  │  Output: { sentences: [...], set_analysis: {...} }  │  │
│  └────────┬───────────────────────────────────────────┘  │
│           │                                              │
│  ┌────────▼───────────────────────────────────────────┐  │
│  │         Hybrid-Analyse-Pipeline                     │  │
│  │                                                     │  │
│  │  1. Satzsegmentierung (regex-basiert)               │  │
│  │  2. Verb-Extraktion (spaCy de_core_news_lg)        │  │
│  │  3. Regelbasierter Check (Verbliste → Stufe)       │  │
│  │  4. Embedding-Klassifikation (SBERT + SVM)          │  │
│  │  5. Ähnlichkeitssuche (Cosine Top-k)               │  │
│  │  6. Set-Analyse (Aggregation)                       │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─────────────────┐  ┌──────────────────────────────┐  │
│  │ Vortrainierte    │  │ Vorberechnete Referenz-DB    │  │
│  │ Modelle          │  │                              │  │
│  │ • SBERT (768d)   │  │ • 3213 Satz-Embeddings      │  │
│  │ • SVM-Typ (K/I/S)│  │ • Taxonomie-Labels          │  │
│  │ • SVM-Tax (1–6)  │  │ • Modul-Metadaten           │  │
│  └─────────────────┘  └──────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## Entscheidung: Wo läuft das Embedding-Modell?

**Entscheidung: Python-Backend (FastAPI)**

| Option | Pro | Contra | Entscheidung |
|--------|-----|--------|-------------|
| Backend-API (FastAPI) | Volle Modellgröße (768d), schnell auf CPU, einfache SVM-Integration | Kein Offline-Betrieb, Netzwerk-Latenz | **Gewählt** |
| ONNX im Browser | Offline-fähig, kein Server nötig | Modell zu groß (278M Params), langsam, kein SVM | Verworfen |
| Vorberechnete Embeddings | Kein Runtime-Embedding nötig | Nur für bekannte Sätze, keine Echtzeit-Analyse neuer Texte | Ergänzend für Referenz-DB |

**Begründung:** T-Systems cross-en-de-roberta hat 278M Parameter — zu groß für den Browser. Das Backend ermöglicht außerdem SVM-Klassifikation, spaCy-Integration und Ähnlichkeitssuche in einem Service.

---

## Hybrides Cascading-Muster

### Datenfluss pro Satz

```
Eingabe-Satz
     │
     ▼
┌─────────────────────────────────────────┐
│ Schritt 1: Satzsegmentierung            │
│ • Regex + Heuristiken (Abkürzungen,     │
│   Aufzählungen, Infinitivkonstruktionen)│
│ • Ergebnis: Liste einzelner Sätze       │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│ Schritt 2: spaCy-Analyse               │
│ • Modell: de_core_news_lg              │
│ • POS-Tagging → Verben extrahieren     │
│ • Lemmatisierung → Grundform           │
│ • Subjekt-Erkennung (Studierende?)     │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│ Schritt 3: Regelbasierte Klassifikation │
│                                         │
│ 3a. Typ-Bestimmung:                     │
│   • Subjekt = Studierende + Verb → K   │
│   • Kein Subjekt/Passiv + Inhalt → I   │
│   • Sonst → S                           │
│                                         │
│ 3b. Taxonomie (nur wenn Typ=K):         │
│   • Lemma in Verbliste?                 │
│     ├─ Eindeutig (1 Stufe) → FERTIG    │
│     │   Konfidenz: 0.95, Quelle: Regel │
│     ├─ Mehrdeutig (>1 Stufe) → weiter  │
│     └─ Nicht gefunden → weiter          │
│   • Lemma in Negativliste?              │
│     → Warnung "vages Verb"              │
└────────────┬────────────────────────────┘
             │ (nur wenn Verb mehrdeutig
             │  oder nicht in Liste)
             ▼
┌─────────────────────────────────────────┐
│ Schritt 4: Embedding-Klassifikation     │
│                                         │
│ • Satz → SBERT-Embedding (768d)         │
│ • SVM-Typ: Embedding → K/I/S           │
│   (nur wenn Schritt 3a unsicher)        │
│ • SVM-Tax: Embedding → Stufe 1–6       │
│   Konfidenz: SVM decision_function      │
│   Quelle: Embedding                     │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│ Schritt 5: Ähnlichkeitssuche            │
│                                         │
│ • Cosine-Similarity zu allen 3213       │
│   Referenz-Embeddings                   │
│ • Top-5 ähnlichste Formulierungen       │
│ • Optional: Filter nach Taxonomiestufe  │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│ Schritt 6: Ergebnis-Zusammenführung     │
│                                         │
│ { typ: "K",                             │
│   taxonomie: 3,                         │
│   konfidenz: 0.87,                      │
│   quelle: "regel" | "embedding",       │
│   verb: "anwenden",                     │
│   verb_hervorhebung: "empfohlen",       │
│   aehnliche: [...top 5...],             │
│   warnungen: ["vages Verb", ...] }      │
└─────────────────────────────────────────┘
```

### Wann Regel, wann Embedding?

| Situation | Methode | Beispiel |
|-----------|---------|---------|
| Verb in Positivliste, eindeutige Stufe | Regel | "nennen" → Stufe 1 |
| Verb in Positivliste, mehrdeutig | Embedding (SVM) | "erkennen" → Stufe 1, 2 oder 4 |
| Verb nicht in Liste, aber Satz hat Subjekt "Studierende" | Embedding (SVM) | "sich auseinandersetzen" → ? |
| Verb in Negativliste | Regel (Warnung) + Embedding | "kennen" → Warnung + SVM-Stufe |
| Kein Verb erkannt / Passivkonstruktion | Embedding (SVM-Typ) | "Grundlagen der BWL" → I |

---

## API-Schnittstelle

### POST /api/analyze

**Request:**
```json
{
  "text": "Die Studierenden können grundlegende Algorithmen implementieren und deren Komplexität analysieren."
}
```

**Response:**
```json
{
  "sentences": [
    {
      "text": "Die Studierenden können grundlegende Algorithmen implementieren und deren Komplexität analysieren.",
      "typ": "K",
      "taxonomie": 4,
      "konfidenz": 0.89,
      "quelle": "embedding",
      "verben": [
        { "verb": "implementieren", "lemma": "implementieren", "stufe_regel": 3, "position": [56, 70] },
        { "verb": "analysieren", "lemma": "analysieren", "stufe_regel": 4, "position": [99, 111] }
      ],
      "warnungen": [],
      "aehnliche": [
        { "satz": "Die Studierenden analysieren die Laufzeit von Algorithmen.", "taxonomie": 4, "similarity": 0.91 },
        { "satz": "Die Studierenden implementieren einfache Sortieralgorithmen.", "taxonomie": 3, "similarity": 0.88 }
      ]
    }
  ],
  "set_analyse": {
    "verteilung": { "1": 0, "2": 0, "3": 1, "4": 1, "5": 0, "6": 0 },
    "abdeckung": 2,
    "max_stufe": 4,
    "empfehlung": "Stufen 1, 2, 5, 6 fehlen. Erwägen Sie Formulierungen auf Bewertungs- oder Erschaffens-Ebene."
  }
}
```

### GET /api/health

Gibt Modell-Info und Status zurück.

---

## Verbliste

Zusammengeführt aus Loth/Konert-Prototyp (76 Verben) und HRK nexus / Bachmann. Bereinigt um den Bug (`Zusammenhänge` ist kein Verb).

**Struktur im Backend:**
```python
VERB_TAXONOMY = {
    "nennen": [1], "auflisten": [1], "wiedergeben": [1], ...
    "erklären": [2], "beschreiben": [2], "zusammenfassen": [2], ...
    "anwenden": [3], "implementieren": [3], "berechnen": [3], ...
    "analysieren": [4], "unterscheiden": [4], "untersuchen": [4], ...
    "beurteilen": [5], "bewerten": [5], "evaluieren": [5], ...
    "entwerfen": [6], "entwickeln": [6], "konzipieren": [6], ...
    # Mehrdeutige Verben:
    "erkennen": [1, 4],
    "vergleichen": [2, 4],
    "planen": [3, 6],
    "kritisieren": [4, 5],
}

BAD_VERBS = ["wissen", "kennen", "erlangen", "beherrschen", "erwerben", "verstehen"]
MODAL_VERBS = ["können", "sollen", "müssen"]
```

---

## Modelle und Daten (Backend-Startup)

Beim Start des Backends werden geladen:

| Artefakt | Beschreibung | Erstellt durch |
|----------|-------------|----------------|
| SBERT-Modell | `T-Systems-onsite/cross-en-de-roberta-sentence-transformer` | HuggingFace (vortrainiert) |
| SVM-Typ | Klassifikator K/I/S, trainiert auf Train-Split | `train_classifiers.py` |
| SVM-Tax | Klassifikator Stufe 1–6, trainiert auf Train-Split (nur K-Sätze) | `train_classifiers.py` |
| Referenz-Embeddings | 3213 vorberechnete Satz-Vektoren (768d) | `build_reference_db.py` |
| Referenz-Metadaten | Typ, Taxonomie, Modulname, Studiengang pro Satz | aus `qualifikationsziele_annotiert.csv` |
| spaCy-Modell | `de_core_news_lg` für POS-Tagging und Lemmatisierung | spaCy (vortrainiert) |

---

## Nuxt-4-Migration

**Entscheidung: Neuaufbau statt inkrementelle Migration**

Der bestehende Prototyp (Nuxt 2 / Vue 2 / Vuetify 2 / Options API) ist nicht inkrementell migrierbar — die Breaking Changes zwischen Vue 2→3 und Vuetify 2→3 betreffen praktisch jede Zeile Code. Was übernommen wird:

| Übernehmen | Nicht übernehmen |
|------------|-----------------|
| UI-Konzept (3-Panel-Layout) | Vue 2 Options API Code |
| Verb-Highlighting-Idee (Farbcodierung) | ContentEditable-Hack (Editable.vue) |
| Verbliste (bereinigt, erweitert) | Vuetify 2 Komponenten |
| Bewertungs-Konzept (Score-Anzeige) | spaCy-Docker-Proxy (wird Backend-intern) |
| Dexie/IndexedDB für Persistenz | Levenshtein-Plugin (ungenutzt) |

**Frontend-Stack:**
- Nuxt 4 (Vue 3 Composition API)
- Vuetify 3 (oder alternativ: Naive UI, PrimeVue)
- Tiptap (ProseMirror-basierter Rich-Text-Editor, ersetzt ContentEditable)
- Pinia (statt Vuex)

---

## Projektstruktur (geplant)

```
code_projects/
├── backend/                     # Python FastAPI
│   ├── main.py                  # FastAPI App + /api/analyze Endpoint
│   ├── pipeline.py              # Hybrid-Analyse-Pipeline (Schritte 1–6)
│   ├── rule_based.py            # Verblisten, Subjekt-Erkennung, Heuristiken
│   ├── embedding.py             # SBERT Encoding + SVM-Klassifikation
│   ├── similarity.py            # Cosine-Similarity-Suche in Referenz-DB
│   ├── models/                  # Trainierte SVM-Modelle (.joblib)
│   ├── data/                    # Referenz-Embeddings (.npy)
│   └── requirements.txt
├── frontend/                    # Nuxt 4
│   ├── app.vue
│   ├── pages/
│   │   └── editor.vue           # Hauptseite
│   ├── components/
│   │   ├── TiptapEditor.vue     # Rich-Text-Editor mit Highlighting
│   │   ├── AnalysisPanel.vue    # Ergebnisse pro Satz
│   │   └── SetAnalysis.vue      # Modul-Übersicht
│   ├── composables/
│   │   └── useAnalysis.ts       # API-Anbindung + Debounce
│   └── nuxt.config.ts
├── train_classifiers.py         # SVM-Training auf Train-Split
├── build_reference_db.py        # Referenz-Embeddings vorberechnen
└── evaluate_embeddings.py       # Modell-Evaluierung (bereits vorhanden)
```

---

## Performance-Abschätzung

| Schritt | Geschätzte Zeit | Anmerkung |
|---------|----------------|-----------|
| Satzsegmentierung | < 1ms | Regex |
| spaCy POS-Tagging | ~5ms/Satz | de_core_news_lg auf CPU |
| Regelbasierter Check | < 1ms | Dict-Lookup |
| SBERT Encoding | ~2ms/Satz | 546 Sätze/s auf CPU (gemessen) |
| SVM-Klassifikation | < 1ms | Trained sklearn |
| Cosine-Similarity (3213 Ref.) | ~1ms | NumPy dot product |
| **Gesamt pro Satz** | **~10ms** | |
| **Typischer Modultext (5–10 Sätze)** | **~50–100ms** | Weit unter 2s-Anforderung (NFA5) |
