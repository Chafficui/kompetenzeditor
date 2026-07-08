# Modellentscheidung: Sentence-Embedding-Modell

## Datum
2026-04-25

## Kontext
Für den hybriden Ansatz (regelbasiert + embedding-basiert) muss ein vortrainiertes Sentence-Embedding-Modell gewählt werden, das deutsche Kompetenzformulierungen aus Modulhandbüchern semantisch repräsentieren kann. Die Embeddings werden für zwei Aufgaben eingesetzt:
1. **Klassifikation** (SVM auf Embeddings): Satztyp (K/I/S) und Taxonomiestufe (1–6)
2. **Ähnlichkeitssuche** (Cosine Similarity): Empfehlungen aus Referenzdatenbank

## Evaluierte Modelle

| Modell | Dim | Sätze/s | Typ-F1 | Tax-F1 |
|--------|-----|---------|--------|--------|
| paraphrase-multilingual-MiniLM-L12-v2 | 384 | 1859 | 0.977 | 0.846 |
| deutsche-telekom/gbert-large-paraphrase-cosine | 1024 | 203 | 0.979 | 0.875 |
| **T-Systems-onsite/cross-en-de-roberta-sentence-transformer** | **768** | **546** | **0.977** | **0.906** |

## Methodik
- **Datensatz**: 3213 Sätze aus 15 FBAI-Modulhandbüchern, LLM-annotiert (typ, taxonomie, konfidenz)
- **Split**: 80/20 stratifiziert nach typ+taxonomie (Seed 42) → 2572 Train, 641 Test
- **Klassifikator**: SVM (RBF-Kernel, C=10, gamma=scale) mit StandardScaler, ohne Hyperparameter-Tuning
- **Metriken**: Weighted F1-Score auf Test-Split
- **Script**: `code_projects/evaluate_embeddings.py`

## Detailergebnisse: T-Systems cross-en-de-roberta (Gewinner)

### Taxonomie-Klassifikation (6 Klassen, nur K-Sätze, n=607 Test)

| Stufe | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------|
| 1 Erinnern | 0.939 | 0.949 | 0.944 | 98 |
| 2 Verstehen | 0.925 | 0.891 | 0.907 | 110 |
| 3 Anwenden | 0.894 | 0.944 | 0.918 | 214 |
| 4 Analysieren | 0.905 | 0.826 | 0.864 | 46 |
| 5 Bewerten | 0.867 | 0.867 | 0.867 | 75 |
| 6 Erschaffen | 0.915 | 0.844 | 0.878 | 64 |
| **Weighted Avg** | **0.906** | **0.906** | **0.906** | **607** |

### Confusion Matrix (Taxonomie)

```
        1     2     3     4     5     6
  1:   93     3     1     1     0     0
  2:    4    98     4     2     2     0
  3:    1     3   202     0     4     4
  4:    0     1     4    38     3     0
  5:    1     1     6     1    65     1
  6:    0     0     9     0     1    54
```

### Typ-Klassifikation (K/I/S, n=641 Test)

| Typ | Precision | Recall | F1 | Support |
|-----|-----------|--------|----|---------|
| K | 0.979 | 1.000 | 0.989 | 607 |
| I | 1.000 | 0.692 | 0.818 | 13 |
| S | 1.000 | 0.571 | 0.727 | 21 |
| **Weighted Avg** | **0.980** | **0.980** | **0.977** | **641** |

## Entscheidung

**T-Systems-onsite/cross-en-de-roberta-sentence-transformer** wird gewählt.

### Begründung
1. **Beste Taxonomie-Klassifikation** (F1 0.906) — schlägt gbert-large (+3.1pp) und MiniLM (+6.0pp)
2. **Guter Kompromiss bei Geschwindigkeit**: 546 Sätze/s — 2.7× schneller als gbert-large, nur 3.4× langsamer als MiniLM
3. **Mittlere Dimensionalität** (768): Guter Kompromiss zwischen Ausdruckskraft und Speicherbedarf für Ähnlichkeitssuche
4. **Cross-linguale Architektur** (EN-DE RoBERTa): Profitiert von englischen Trainingskorpora, die im akademischen Bereich reichhaltiger sind
5. **Schlägt die Konkurrenz konsistent** in jeder einzelnen Taxonomiestufe

### Limitationen
- Typ-Klassifikation (K/I/S) ist bei allen Modellen ähnlich gut (~98%) — die Aufgabe ist zu leicht für eine Differenzierung
- I- und S-Klassen haben sehr wenig Test-Support (13 bzw. 21) → Recall-Werte dort weniger belastbar
- Evaluierung ohne Hyperparameter-Tuning (SVM C=10 fix) — finale Ergebnisse können noch besser werden mit Cross-Validation
