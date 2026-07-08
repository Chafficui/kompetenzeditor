#!/usr/bin/env python3
"""
LLM-basierte Vorannotation v2: erweitertes Schema.
Annotiert jeden Satz mit:
  - typ: K/I/S
  - taxonomie: Liste von Stufen (z.B. [3,5]) — Mehrfachwerte möglich
  - qualitaet: gut/akzeptabel/schlecht (Formulierungsqualität)
  - konfidenz: 0.0-1.0

Nutzung:
  export ANTHROPIC_API_KEY=sk-ant-...
  python3 vorannotation_v2.py [--batch-size 20] [--model claude-sonnet-4-6]
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import anthropic

SYSTEM_PROMPT = """Du bist ein Experte für Hochschuldidaktik und die Taxonomie nach Anderson & Krathwohl (2001).
Deine Aufgabe: Sätze aus Modulhandbüchern deutscher Hochschulen annotieren.

## Annotationsschema

### Satztyp (typ)
- K = Kompetenzformulierung: Satz beschreibt ein Lernergebnis der Studierenden mit beobachtbarem Handlungsverb
- I = Inhaltsbeschreibung: Satz beschreibt Lehrinhalte, Themen oder Modulbestandteile ohne Handlungsergebnis
- S = Sonstiges: Organisatorisches, Einleitungssätze, Fragmente

### Taxonomiestufe (nur wenn typ=K) — MEHRFACHWERTE MÖGLICH
1 = Erinnern (nennen, auflisten, wiedergeben, benennen, identifizieren)
2 = Verstehen (erklären, beschreiben, zusammenfassen, interpretieren, vergleichen)
3 = Anwenden (anwenden, berechnen, durchführen, implementieren, lösen, einsetzen)
4 = Analysieren (analysieren, unterscheiden, untersuchen, strukturieren, zuordnen)
5 = Bewerten (beurteilen, bewerten, evaluieren, überprüfen, einschätzen, reflektieren)
6 = Erschaffen (entwerfen, entwickeln, konzipieren, konstruieren, gestalten, planen)

Ein Satz kann MEHRERE Taxonomiestufen haben, wenn er mehrere Verben auf verschiedenen Stufen enthält.
Beispiel: "Die Studierenden analysieren Algorithmen und wenden diese an" → [3, 4]
Gib die Stufen als sortierte Liste an: [niedrigste, ..., höchste]

### Qualität der Formulierung (qualitaet)
- gut: Klar formuliert mit beobachtbarem Handlungsverb, konkretem Gegenstand, Studierende als Subjekt
- akzeptabel: Verständlich, aber nicht ideal (z.B. vage Verben wie "kennen", fehlendes Subjekt, zu lang)
- schlecht: Nicht messbar, unklar, grammatisch problematisch, oder gar keine Kompetenzformulierung trotz K-Klassifikation

### Wichtige Regeln
- "kennen" allein = Stufe 1; "können" + Infinitiv = Stufe des Infinitivverbs
- "verstehen" = Stufe 2, außer Kontext zeigt klar etwas anderes
- "sind in der Lage" ist taxonomisch neutral → Stufe des nachfolgenden Verbs
- Kontextabhängigkeit beachten: "erkennen" kann Stufe 1, 4 oder 5 sein je nach Kontext
- Stufe 6 nur bei genuiner Neuschöpfung, nicht für bloßes Zusammenstellen
- "erstellen eine Zusammenfassung" = Stufe 2, NICHT Stufe 6
- "entwickeln ein Verständnis" = Stufe 2, NICHT Stufe 6"""

USER_PROMPT_TEMPLATE = """Annotiere die folgenden Sätze aus Modulhandbüchern. Antworte NUR mit einem JSON-Array.

Für jeden Satz:
{{"id": <index>, "typ": "K"|"I"|"S", "taxonomie": [1-6] oder null, "qualitaet": "gut"|"akzeptabel"|"schlecht", "konfidenz": 0.0-1.0}}

Beachte:
- taxonomie ist eine LISTE (z.B. [3] oder [3,5]), nicht eine einzelne Zahl
- qualitaet bewertet die Formulierungsqualität, nicht den Inhalt
- konfidenz gibt an, wie sicher du dir bei der gesamten Annotation bist

Sätze:
{sentences}

Antworte ausschließlich mit dem JSON-Array, ohne Markdown-Formatierung oder andere Texte."""


def build_sentence_block(batch: list[dict], start_idx: int) -> str:
    lines = []
    for i, row in enumerate(batch):
        idx = start_idx + i
        lines.append(f"[{idx}] ({row.get('hochschule', '?')}/{row['modul_id']}) {row['satz']}")
    return "\n".join(lines)


def parse_response(text: str, expected_count: int) -> list[dict] | None:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    try:
        result = json.loads(text)
        if isinstance(result, list) and len(result) == expected_count:
            return result
    except json.JSONDecodeError:
        pass

    import re
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, list) and len(result) == expected_count:
                return result
        except json.JSONDecodeError:
            pass

    return None


def annotate_batch(client: anthropic.Anthropic, batch: list[dict], start_idx: int,
                   model: str) -> list[dict]:
    sentence_block = build_sentence_block(batch, start_idx)
    prompt = USER_PROMPT_TEMPLATE.format(sentences=sentence_block)

    for attempt in range(3):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text
            annotations = parse_response(text, len(batch))

            if annotations:
                return annotations

            print(f"    Warnung: Parsing fehlgeschlagen (Versuch {attempt+1})")
            if attempt == 2:
                print(f"    Rohantwort: {text[:300]}")

        except anthropic.RateLimitError:
            wait = 30 * (attempt + 1)
            print(f"    Rate limit, warte {wait}s...")
            time.sleep(wait)
        except anthropic.APIError as e:
            print(f"    API-Fehler: {e}")
            if attempt == 2:
                raise

    return [{"id": start_idx + i, "typ": "?", "taxonomie": None, "qualitaet": "schlecht", "konfidenz": 0.0}
            for i in range(len(batch))]


def main():
    parser = argparse.ArgumentParser(description="LLM-Vorannotation v2 (erweitertes Schema)")
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--model", default="claude-sonnet-4-6")
    parser.add_argument("--input", required=True, help="Input CSV (unannotierte Sätze)")
    parser.add_argument("--output", required=True, help="Output CSV")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Filter to unannotated rows only
    unannotated = [r for r in rows if not r.get('typ')]
    if not unannotated:
        print("Keine unannotierten Sätze gefunden.")
        return

    total = len(unannotated)
    print(f"Vorannotation v2: {total} Sätze, Batch-Größe {args.batch_size}, Modell {args.model}")

    client = anthropic.Anthropic()

    annotated = []
    stats = {"K": 0, "I": 0, "S": 0, "?": 0}
    qual_stats = {"gut": 0, "akzeptabel": 0, "schlecht": 0}

    for batch_start in range(0, total, args.batch_size):
        batch = unannotated[batch_start:batch_start + args.batch_size]
        batch_num = batch_start // args.batch_size + 1
        total_batches = (total + args.batch_size - 1) // args.batch_size

        print(f"  Batch {batch_num}/{total_batches} "
              f"(Sätze {batch_start+1}-{batch_start+len(batch)})...", end=" ", flush=True)

        annotations = annotate_batch(client, batch, batch_start, args.model)

        for row, ann in zip(batch, annotations):
            typ = ann.get("typ", "?")
            tax = ann.get("taxonomie")
            qual = ann.get("qualitaet", "akzeptabel")
            conf = ann.get("konfidenz", 0.0)

            # Normalize taxonomie to semicolon-separated string
            if isinstance(tax, list):
                tax_str = ";".join(str(t) for t in sorted(tax))
            elif tax is not None:
                tax_str = str(tax)
            else:
                tax_str = ""

            stats[typ] = stats.get(typ, 0) + 1
            qual_stats[qual] = qual_stats.get(qual, 0) + 1

            annotated.append({
                **row,
                "typ": typ,
                "taxonomie": tax_str,
                "qualitaet": qual,
                "konfidenz": f"{conf:.2f}",
            })

        k_count = sum(1 for a in annotations if a.get("typ") == "K")
        print(f"OK ({k_count}K/{len(batch)-k_count}rest)")

        # Save intermediate every 5 batches
        if batch_num % 5 == 0 or batch_start + len(batch) >= total:
            with open(args.output, "w", newline="", encoding="utf-8") as f:
                fieldnames = list(annotated[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(annotated)

        time.sleep(0.5)

    print(f"\n{'='*60}")
    print(f"ERGEBNIS: {len(annotated)} Sätze annotiert")
    print(f"\nKlassifikation: {dict(stats)}")
    print(f"Qualität: {dict(qual_stats)}")
    print(f"\nOutput: {args.output}")


if __name__ == "__main__":
    main()
