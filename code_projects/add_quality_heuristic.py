#!/usr/bin/env python3
"""
Heuristische Qualitätsbewertung für bestehende HS-Fulda-Sätze.
Ergänzt die `qualitaet`-Spalte basierend auf einfachen Regeln:
  - gut: Hat Subjekt ("Die Studierenden") + beobachtbares Verb + fachlichen Gegenstand
  - akzeptabel: Hat Verb, aber vage ("kennen", "wissen") oder fehlendes Subjekt
  - schlecht: Kein Verb, zu kurz, oder gar keine Kompetenzformulierung
"""

import csv
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

GUTE_VERBEN = {
    "implementieren", "berechnen", "analysieren", "entwerfen", "entwickeln",
    "anwenden", "durchführen", "lösen", "konstruieren", "gestalten",
    "bewerten", "beurteilen", "evaluieren", "konzipieren", "programmieren",
    "modellieren", "simulieren", "testen", "validieren", "dokumentieren",
    "interpretieren", "vergleichen", "klassifizieren", "strukturieren",
    "planen", "erstellen", "einsetzen", "demonstrieren", "überprüfen",
}

VAGE_VERBEN = {
    "kennen", "wissen", "verstehen", "können", "haben", "verfügen",
    "besitzen", "sein", "werden",
}


def assess_quality(satz: str, typ: str) -> str:
    satz_lower = satz.lower()
    words = set(re.findall(r'\b\w+\b', satz_lower))

    if typ != "K":
        return "schlecht" if typ == "S" else "akzeptabel"

    if len(satz) < 20:
        return "schlecht"

    has_subject = any(p in satz_lower for p in [
        "die studierenden", "studierende", "sie sind", "sie können",
        "absolvent", "teilnehm",
    ])

    has_good_verb = bool(words & GUTE_VERBEN)
    has_vague_verb = bool(words & VAGE_VERBEN)

    # Check for measurable action
    has_infinitiv = bool(re.search(r'zu \w+en\b', satz_lower))

    if has_subject and has_good_verb:
        return "gut"
    elif has_good_verb or (has_subject and has_infinitiv):
        return "gut"
    elif has_subject and has_vague_verb:
        return "akzeptabel"
    elif has_vague_verb or has_infinitiv:
        return "akzeptabel"
    else:
        return "schlecht"


def main():
    input_path = DATA_DIR / "qualifikationsziele_annotiert.csv"
    with open(input_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Bewerte {len(rows)} HS-Fulda-Sätze...")

    for r in rows:
        r["qualitaet"] = assess_quality(r["satz"], r["typ"])
        r["hochschule"] = "Hochschule Fulda"

    from collections import Counter
    qual_counts = Counter(r["qualitaet"] for r in rows)
    print(f"\nQualitätsverteilung:")
    for q in ["gut", "akzeptabel", "schlecht"]:
        print(f"  {q}: {qual_counts[q]} ({qual_counts[q]/len(rows)*100:.1f}%)")

    # Save
    output_path = DATA_DIR / "qualifikationsziele_annotiert_v2.csv"
    fieldnames = ["studiengang", "hochschule", "modul_id", "modulname", "satz_nr", "satz",
                  "typ", "taxonomie", "qualitaet", "konfidenz", "split"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nOutput: {output_path}")


if __name__ == "__main__":
    main()
