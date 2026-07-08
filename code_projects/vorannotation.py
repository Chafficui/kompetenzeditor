#!/usr/bin/env python3
"""
LLM-basierte Vorannotation der Qualifikationsziele.
Annotiert jeden Satz mit:
  - typ: K (Kompetenzformulierung), I (Inhaltsbeschreibung), S (Sonstiges)
  - taxonomie: 1-6 (Anderson/Krathwohl), nur wenn typ=K
  - konfidenz: 0.0-1.0

Nutzung:
  export ANTHROPIC_API_KEY=sk-ant-...
  python3 vorannotation.py [--batch-size 20] [--model claude-sonnet-4-6] [--limit 50]
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

### Taxonomiestufe (nur wenn typ=K)
1 = Erinnern: Wissen abrufen (nennen, auflisten, wiedergeben, benennen, identifizieren)
2 = Verstehen: Bedeutung konstruieren (erklären, beschreiben, zusammenfassen, interpretieren, vergleichen, diskutieren)
3 = Anwenden: Verfahren ausführen (anwenden, berechnen, durchführen, implementieren, benutzen, lösen, einsetzen)
4 = Analysieren: Bestandteile und Beziehungen erkennen (analysieren, unterscheiden, untersuchen, strukturieren, zuordnen)
5 = Bewerten: Urteile fällen (beurteilen, bewerten, evaluieren, überprüfen, einschätzen, reflektieren, kritisieren)
6 = Erschaffen: Neues Ganzes schaffen (entwerfen, entwickeln, konzipieren, konstruieren, gestalten, planen)

### Wichtige Regeln
- "kennen" allein = Stufe 1; "können" + Infinitiv = Stufe des Infinitivverbs
- "verstehen" = Stufe 2, außer Kontext zeigt klar etwas anderes
- "sind in der Lage" ist taxonomisch neutral → Stufe des nachfolgenden Verbs
- Bei mehreren Verben: höchste Stufe zählt
- Kontextabhängigkeit beachten: "erkennen" kann Stufe 1, 4 oder 5 sein je nach Kontext
- Stufe 6 nur bei genuiner Neuschöpfung, nicht für bloßes Zusammenstellen
- Infinitivkonstruktionen ("...zu implementieren") zählen als K wenn sie ein Handlungsergebnis beschreiben
- "erstellen eine Zusammenfassung" = Stufe 2 (Zusammenfassen), NICHT Stufe 6
- "entwickeln ein Verständnis" = Stufe 2, NICHT Stufe 6"""

USER_PROMPT_TEMPLATE = """Annotiere die folgenden Sätze aus Modulhandbüchern. Antworte NUR mit einem JSON-Array.

Für jeden Satz:
{{"id": <index>, "typ": "K"|"I"|"S", "taxonomie": 1-6 oder null, "konfidenz": 0.0-1.0}}

Die Konfidenz gibt an, wie sicher du dir bei der Annotation bist (1.0 = sehr sicher, 0.5 = unsicher).

Sätze:
{sentences}

Antworte ausschließlich mit dem JSON-Array, ohne Markdown-Formatierung oder andere Texte."""


def build_sentence_block(batch: list[dict], start_idx: int) -> str:
    lines = []
    for i, row in enumerate(batch):
        idx = start_idx + i
        lines.append(f"[{idx}] ({row['modul_id']}) {row['satz']}")
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

    # Try to extract JSON array from response
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

            print(f"    Warnung: Parsing fehlgeschlagen (Versuch {attempt+1}), Retry...")
            if attempt == 2:
                print(f"    Rohantwort: {text[:200]}")

        except anthropic.RateLimitError:
            wait = 30 * (attempt + 1)
            print(f"    Rate limit, warte {wait}s...")
            time.sleep(wait)
        except anthropic.APIError as e:
            print(f"    API-Fehler: {e}")
            if attempt == 2:
                raise

    # Fallback: return empty annotations
    return [{"id": start_idx + i, "typ": "?", "taxonomie": None, "konfidenz": 0.0}
            for i in range(len(batch))]


def main():
    parser = argparse.ArgumentParser(description="LLM-Vorannotation der Qualifikationsziele")
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--model", default="claude-sonnet-4-6")
    parser.add_argument("--limit", type=int, default=None,
                        help="Nur die ersten N Sätze annotieren (für Tests)")
    parser.add_argument("--input", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    base_dir = Path(__file__).parent.parent
    input_csv = Path(args.input) if args.input else base_dir / "data" / "qualifikationsziele.csv"
    output_csv = Path(args.output) if args.output else base_dir / "data" / "qualifikationsziele_annotiert.csv"

    with open(input_csv, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if args.limit:
        rows = rows[:args.limit]

    total = len(rows)
    print(f"Vorannotation: {total} Sätze, Batch-Größe {args.batch_size}, Modell {args.model}")
    print(f"Input:  {input_csv}")
    print(f"Output: {output_csv}")

    # Check for existing partial results
    annotated = []
    start_from = 0
    if output_csv.exists():
        with open(output_csv, encoding="utf-8") as f:
            existing = list(csv.DictReader(f))
        if existing and len(existing) < total:
            annotated = existing
            start_from = len(existing)
            print(f"Fortsetzen ab Satz {start_from} ({len(existing)} bereits annotiert)")
        elif existing and len(existing) >= total:
            print(f"Bereits vollständig annotiert ({len(existing)} Sätze). Abbruch.")
            return

    client = anthropic.Anthropic()

    batches = []
    for i in range(start_from, total, args.batch_size):
        batch = rows[i:i + args.batch_size]
        batches.append((i, batch))

    print(f"\n{len(batches)} API-Calls nötig\n")

    stats = {"K": 0, "I": 0, "S": 0, "?": 0}
    tax_stats = {str(i): 0 for i in range(1, 7)}
    low_conf = 0

    for batch_num, (start_idx, batch) in enumerate(batches):
        print(f"  Batch {batch_num+1}/{len(batches)} "
              f"(Sätze {start_idx+1}-{start_idx+len(batch)})...", end=" ", flush=True)

        annotations = annotate_batch(client, batch, start_idx, args.model)

        for row, ann in zip(batch, annotations):
            typ = ann.get("typ", "?")
            tax = ann.get("taxonomie")
            conf = ann.get("konfidenz", 0.0)

            stats[typ] = stats.get(typ, 0) + 1
            if typ == "K" and tax:
                tax_stats[str(tax)] = tax_stats.get(str(tax), 0) + 1
            if conf < 0.7:
                low_conf += 1

            annotated.append({
                **row,
                "typ": typ,
                "taxonomie": str(tax) if tax else "",
                "konfidenz": f"{conf:.2f}",
            })

        print(f"OK ({sum(1 for a in annotations if a.get('typ') == 'K')}K/"
              f"{sum(1 for a in annotations if a.get('typ') == 'I')}I/"
              f"{sum(1 for a in annotations if a.get('typ') == 'S')}S)")

        # Save intermediate results every 5 batches
        if (batch_num + 1) % 5 == 0 or batch_num == len(batches) - 1:
            with open(output_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "studiengang", "modul_id", "modulname", "satz_nr", "satz",
                    "typ", "taxonomie", "konfidenz"
                ])
                writer.writeheader()
                writer.writerows(annotated)

        time.sleep(0.5)

    # Final statistics
    total_done = len(annotated)
    print(f"\n{'='*60}")
    print(f"ERGEBNIS: {total_done} Sätze annotiert")
    print(f"\nKlassifikation:")
    for t in ["K", "I", "S", "?"]:
        count = stats.get(t, 0)
        pct = count / total_done * 100 if total_done else 0
        print(f"  {t}: {count:4d} ({pct:.1f}%)")

    print(f"\nTaxonomie (nur K-Sätze):")
    for level in range(1, 7):
        count = tax_stats.get(str(level), 0)
        label = ["", "Erinnern", "Verstehen", "Anwenden", "Analysieren", "Bewerten", "Erschaffen"][level]
        print(f"  {level} {label}: {count:4d}")

    print(f"\nNiedrige Konfidenz (<0.7): {low_conf} Sätze ({low_conf/total_done*100:.1f}%)")
    print(f"\nOutput: {output_csv}")


if __name__ == "__main__":
    main()
