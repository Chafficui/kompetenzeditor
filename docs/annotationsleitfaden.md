# Annotationsleitfaden: Gold-Standard für Kompetenzformulierungen

## 1. Zweck

Dieser Leitfaden definiert das Annotationsschema für den Gold-Standard-Datensatz der Masterarbeit. Die Annotationen dienen als Ground Truth für die Evaluation dreier Ansätze (regelbasiert, embedding-basiert, hybrid) in zwei Dimensionen:

1. **Klassifikation**: Ist der Satz eine Kompetenzformulierung?
2. **Taxonomie-Zuordnung**: Welche kognitive Prozessstufe nach Anderson & Krathwohl (2001)?

## 2. Annotationskategorien

### 2.1 Satztyp (`typ`)

| Label | Bezeichnung | Definition |
|-------|------------|------------|
| `K` | Kompetenzformulierung | Ein Satz, der ein intendiertes Lernergebnis beschreibt: Studierende als (implizites oder explizites) Subjekt + beobachtbares/messbares Handlungsverb + fachlicher Gegenstand. |
| `I` | Inhaltsbeschreibung | Ein Satz, der Lehrinhalte, Themen oder Modulbeschreibungen wiedergibt, ohne ein konkretes Handlungsergebnis der Studierenden zu formulieren. |
| `S` | Sonstiges | Organisatorische Informationen, Einleitungssätze, Aufzählungsreste oder nicht zuordenbare Fragmente. |

### 2.2 Taxonomiestufe (`taxonomie`, nur wenn `typ = K`)

Die sechs kognitiven Prozessstufen nach Anderson & Krathwohl (2001), aufsteigend geordnet:

| Stufe | Bezeichnung | Kernprozess | Beispielverben (deutsch) |
|-------|------------|-------------|--------------------------|
| 1 | Erinnern | Relevantes Wissen aus dem Langzeitgedächtnis abrufen | wiedergeben, nennen, auflisten, benennen, identifizieren, reproduzieren, erinnern |
| 2 | Verstehen | Bedeutung von Informationen konstruieren (mündlich, schriftlich, grafisch) | erklären, beschreiben, zusammenfassen, interpretieren, klassifizieren, vergleichen, erläutern, diskutieren, darstellen |
| 3 | Anwenden | Ein Verfahren in einer gegebenen Situation ausführen oder nutzen | anwenden, berechnen, durchführen, implementieren, benutzen, lösen, demonstrieren, umsetzen, einsetzen |
| 4 | Analysieren | Material in Bestandteile zerlegen und Beziehungen zwischen Teilen und zur Gesamtstruktur erkennen | analysieren, unterscheiden, differenzieren, untersuchen, strukturieren, organisieren, zuordnen |
| 5 | Bewerten | Urteile auf Basis von Kriterien und Standards fällen | beurteilen, bewerten, evaluieren, überprüfen, kritisieren, einschätzen, abwägen, reflektieren |
| 6 | Erschaffen | Elemente zu einem neuen, kohärenten Ganzen zusammenfügen; einen originären Entwurf erstellen | entwerfen, entwickeln, konzipieren, konstruieren, gestalten, planen (eigenständig), produzieren, erstellen |

## 3. Entscheidungsregeln

### 3.1 Klassifikation (K vs. I vs. S)

**Regel 1 — Handlungsverb-Test:**
Enthält der Satz ein Verb, das eine beobachtbare/messbare Handlung der Studierenden beschreibt?
- Ja → `K` (Kompetenzformulierung)
- Nein → weiter zu Regel 2

**Regel 2 — Inhalts-Test:**
Beschreibt der Satz fachliche Inhalte, Themen, Methoden oder Modulbestandteile?
- Ja → `I` (Inhaltsbeschreibung)
- Nein → `S` (Sonstiges)

**Regel 3 — Subjekt-Test (Zweifelsfälle):**
Sind Studierende das (explizite oder implizite) Subjekt der Handlung?
- "Die Studierenden analysieren..." → `K`
- "Das Modul vermittelt..." → `I` (Modul ist Subjekt, nicht Studierende)
- "Es werden Grundlagen behandelt..." → `I` (passivische Inhaltsbeschreibung)

**Regel 4 — Infinitivkonstruktionen:**
Sätze in Infinitivform nach "sind in der Lage, ..." oder als Aufzählungspunkte:
- "mathematische Modelle zu entwickeln und anzuwenden" → `K` (implizites Subjekt = Studierende)
- Auch ohne explizites Subjekt zählen diese als Kompetenzformulierung, wenn sie aus dem Qualifikationsziele-Abschnitt stammen und eine messbare Handlung beschreiben.

### 3.2 Taxonomie-Zuordnung

**Regel 5 — Primäres Handlungsverb:**
Die Taxonomiestufe wird primär durch das Hauptverb des Satzes bestimmt. Bei mehreren Verben gilt das hierarchisch höchste.
- "Die Studierenden **analysieren** Algorithmen und **wenden** diese an" → Stufe 4 (Analysieren > Anwenden)

**Regel 6 — Kontextabhängigkeit (Stanny-Prinzip):**
Viele Verben sind mehrdeutig (vgl. Stanny 2016: "erkennen" erscheint auf 3 Stufen). Die Zuordnung muss den Satzkontext berücksichtigen:
- "Die Studierenden **erkennen** die Fachbegriffe wieder" → Stufe 1 (Wiedererkennen = Erinnern)
- "Die Studierenden **erkennen** Muster in Datensätzen" → Stufe 4 (Muster erkennen = Analysieren)
- "Die Studierenden **erkennen** die Grenzen des Verfahrens" → Stufe 5 (Grenzen erkennen = Bewerten)

**Regel 7 — "kennen/können/wissen":**
Diese Verben sind häufig, aber taxonomisch unterspezifiziert:
- "kennen die Grundlagen" → Stufe 1 (bloßes Wissen)
- "kennen und können anwenden" → Stufe 3 (Anwenden überwiegt)
- "können beurteilen" → Stufe 5 (Bewerten)
- Im Zweifel: "kennen" allein = Stufe 1; "können" + Infinitiv = Stufe des Infinitivverbs

**Regel 8 — "verstehen":**
"Verstehen" ist oft unterspezifiziert, wird aber als Stufe 2 kodiert, es sei denn der Kontext zeigt klar eine andere Stufe:
- "verstehen die Grundlagen" → Stufe 2
- "verstehen und können erklären" → Stufe 2

**Regel 9 — "sind in der Lage" / "sind fähig":**
Diese Rahmenformulierungen sind taxonomisch neutral. Die Stufe wird durch das nachfolgende Verb bestimmt:
- "sind in der Lage, Algorithmen zu **implementieren**" → Stufe 3 (Anwenden)
- "sind in der Lage, Ergebnisse kritisch zu **beurteilen**" → Stufe 5 (Bewerten)

**Regel 10 — Stufe 6 nur bei genuiner Neuschöpfung:**
Stufe 6 (Erschaffen) wird nur vergeben, wenn der Satz eine eigenständige, kreative Syntheseleistung beschreibt — nicht für das bloße Zusammenstellen bekannter Elemente:
- "entwerfen eine Softwarearchitektur für ein gegebenes Problem" → Stufe 6
- "erstellen eine Zusammenfassung der Ergebnisse" → Stufe 2 (Zusammenfassen)
- "entwickeln eigene Lösungsstrategien" → Stufe 6
- "entwickeln ein Verständnis für..." → Stufe 2

## 4. Grenzfälle und Konventionen

### 4.1 Mischsätze
Enthält ein Satz sowohl Kompetenz- als auch Inhaltsaspekte, wird nach dem dominanten Charakter entschieden:
- "Die Studierenden lernen Sortieralgorithmen kennen und **implementieren** diese." → `K`, Stufe 3 (die Handlung überwiegt)
- "Das Modul behandelt Datenstrukturen; die Studierenden sollen diese benennen können." → `K`, Stufe 1 (Kompetenzformulierung am Ende)

### 4.2 Einleitungssätze
Einleitende Sätze ohne Handlungsverb:
- "Nach erfolgreicher Teilnahme an dem Modul..." → `S`
- "Die Studierenden verfügen über folgende Kompetenzen:" → `S`

### 4.3 Passive/unpersönliche Formulierungen
- "Es werden Kenntnisse in Datenbanken vermittelt." → `I`
- "Grundlagen der Programmierung werden behandelt." → `I`

### 4.4 Englischsprachige Sätze
Werden genauso annotiert wie deutsche. Die Taxonomie-Verben im Englischen orientieren sich an der Anderson/Krathwohl-Originalterminologie (remember, understand, apply, analyze, evaluate, create).

### 4.5 Mehrfach auftretende Module
Manche Module erscheinen in mehreren Studiengängen oder in deutsch/englischer Version. Jeder Satz wird einzeln annotiert, auch bei Duplikaten.

### 4.6 Mehrfach-Taxonomiestufen
Ein Satz kann mehrere Taxonomiestufen haben, wenn er mehrere Handlungsverben auf verschiedenen Stufen enthält:
- "Die Studierenden **analysieren** Algorithmen und **wenden** diese an" → Stufen 3;4
- "Die Studierenden **beurteilen** Verfahren und **entwickeln** eigene Lösungen" → Stufen 5;6
- Bei nur einem Verb oder Verben auf derselben Stufe: nur eine Stufe

### 4.7 Formulierungsqualität
Jeder Satz erhält zusätzlich eine Bewertung der Formulierungsqualität:

| Qualität | Definition | Beispiel |
|----------|-----------|----------|
| `gut` | Klares, beobachtbares Handlungsverb + konkreter Gegenstand + Studierende als Subjekt | "Die Studierenden implementieren rekursive Algorithmen in Java." |
| `akzeptabel` | Verständlich, aber nicht ideal: vage Verben, fehlendes Subjekt, zu lang, oder unterspezifiziert | "Die Studierenden kennen die Grundlagen der Informatik." |
| `schlecht` | Nicht messbar, unklar, grammatisch problematisch, oder Tabellenartefakt | "Grundlagen der Programmierung" |

## 5. Annotationsformat

Das Ausgabeformat enthält folgende Spalten:

```
studiengang, hochschule, modul_id, modulname, satz_nr, satz, typ, taxonomie, qualitaet, konfidenz, split
```

- `studiengang`: Name des Studiengangs (z.B. "Angewandte Informatik (B.Sc.)")
- `hochschule`: Name der Hochschule (z.B. "Hochschule Fulda", "TU Darmstadt")
- `typ`: K | I | S
- `taxonomie`: Semikolon-getrennte Stufenliste (z.B. "3", "3;5") | leer (wenn typ ≠ K)
- `qualitaet`: gut | akzeptabel | schlecht
- `konfidenz`: 0.0–1.0 (LLM-Konfidenz der Vorannotation)
- `split`: train | test (stratifiziert, 80/20)

## 6. Annotationsprozess

### Phase 1: LLM-Vorannotation
- Claude (Sonnet) annotiert alle Sätze automatisch mit `typ`, `taxonomie`, `qualitaet` und `konfidenz`
- Datensatz: 5600+ Sätze aus 4 Hochschulen (HS Fulda, TU Darmstadt, TH Mittelhessen, Uni Kassel)
- Konfidenzwert (0.0–1.0) des LLM wird mitgespeichert
- Dient als Ausgangsbasis, NICHT als Ground Truth

### Phase 2: Manuelle Validierung
- Stratifizierte Stichprobe von ~250–300 Sätzen (nach Hochschule, Taxonomiestufe, Konfidenz)
- Manuelle Prüfung und ggf. Korrektur der LLM-Vorannotation
- Schwerpunkt auf Grenzfällen und Sätzen mit niedriger LLM-Konfidenz

### Phase 3: Inter-Annotator-Reliabilität
- Zweiter Annotator annotiert ~100 Sätze unabhängig (Subset der Stichprobe)
- Cohen's Kappa berechnen für drei Dimensionen:
  - Klassifikation (K/I/S): Ziel κ ≥ 0.7
  - Taxonomie (Primärstufe): Ziel κ ≥ 0.6
  - Qualität (gut/akzeptabel/schlecht): Ziel κ ≥ 0.5
- Bei niedrigem Kappa: Diskussion der Abweichungen, Leitfaden-Revision, erneute Annotation

## 7. Qualitätskriterien für den Gold-Standard

| Kriterium | Zielwert |
|-----------|----------|
| Gesamtdatensatz | ≥ 5000 Sätze |
| Hochschulen | ≥ 3 verschiedene |
| Fachbereiche | ≥ 3 verschiedene |
| Stichprobengröße (manuell validiert) | ≥ 250 Sätze |
| Anteil K-Sätze in Stichprobe | ~70–80% |
| Taxonomie-Abdeckung | Alle 6 Stufen mit ≥ 10 Sätzen |
| Inter-Annotator κ (Klassifikation) | ≥ 0.7 |
| Inter-Annotator κ (Taxonomie) | ≥ 0.6 |
| Inter-Annotator κ (Qualität) | ≥ 0.5 |
| Schwierigkeitsverteilung | ~50% Standard, ~30% Grenzfälle, ~20% Nicht-Kompetenz |
