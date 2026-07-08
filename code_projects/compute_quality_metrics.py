"""
Berechnet automatische Qualitätsindikatoren für Kompetenzformulierungen
basierend auf den HRK-nexus-Leitlinien.

Kriterien:
  Q1: Beobachtbares Verb vorhanden (aus Verbliste)
  Q2: Eindeutigkeit (genau ein Hauptverb / eine Stufe)
  Q3: Subjekt-Nennung (Studierende / Sie / impliziert)
  Q4: Spezifität (Satz enthält fachlichen Gegenstand, Proxy: Satzlänge > 40 Zeichen)
  Q5: Keine vagen Verben (können, sollen, werden als Vollverb)
  Q6: Granularität (ein Lernergebnis pro Satz, Proxy: max. ein empfohlenes Verb)
"""

import csv
import json
import re
import sys
from pathlib import Path

DATA_CSV = Path(__file__).parent.parent / "data" / "goldstandard.csv"
VERBLISTE = Path(__file__).parent / "backend" / "data" / "verbliste.json"

SUBJEKT_PATTERN = re.compile(
    r"\b(die studierenden|studierende|der student|die studentin|"
    r"sie\b|absolvent|absolventin|lernende|teilnehmer)",
    re.IGNORECASE,
)

VAGE_VERBEN = {"können", "sollen", "werden", "wissen", "kennen", "lernen", "erfahren"}


def load_verbliste():
    with open(VERBLISTE) as f:
        data = json.load(f)
    verben = set()
    for stufe, verb_list in data.get("empfohlen", {}).items():
        for v in verb_list:
            verben.add(v.lower())
    for verb, stufen in data.get("mehrdeutig", {}).items():
        verben.add(verb.lower())
    return verben


def compute_quality(satz, typ, taxonomie, verbliste):
    """Bewertet einen Satz nach den 6 automatisierbaren Qualitätskriterien."""
    satz_lower = satz.lower()
    words = satz_lower.split()

    # Q1: Beobachtbares Verb vorhanden
    q1 = any(w.rstrip(".,;:!?") in verbliste for w in words) if typ == "K" else False

    # Q2: Eindeutigkeit (genau eine Taxonomiestufe)
    tax_values = [t.strip() for t in str(taxonomie).split(";") if t.strip()] if taxonomie else []
    q2 = len(tax_values) == 1 if typ == "K" else True

    # Q3: Subjekt-Nennung
    q3 = bool(SUBJEKT_PATTERN.search(satz))

    # Q4: Spezifität (Proxy: Satzlänge > 40 Zeichen)
    q4 = len(satz) > 40

    # Q5: Keine vagen Verben als Hauptverb
    q5 = not any(w.rstrip(".,;:!?") in VAGE_VERBEN for w in words[:5])

    # Q6: Granularität (max. 2 Verbliste-Treffer)
    verb_count = sum(1 for w in words if w.rstrip(".,;:!?") in verbliste)
    q6 = verb_count <= 2

    score = sum([q1, q2, q3, q4, q5, q6])
    return {
        "q1_verb": q1,
        "q2_eindeutig": q2,
        "q3_subjekt": q3,
        "q4_spezifisch": q4,
        "q5_nicht_vage": q5,
        "q6_granular": q6,
        "score": score,
        "score_pct": round(score / 6 * 100, 1),
    }


def main():
    verbliste = load_verbliste()
    print(f"Verbliste: {len(verbliste)} Verben geladen")

    rows = []
    with open(DATA_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"Datensatz: {len(rows)} Sätze")

    # Nur K-Sätze für Qualitätsanalyse
    k_rows = [r for r in rows if r.get("typ", "").strip() == "K"]
    print(f"K-Sätze: {len(k_rows)}")

    results = []
    for row in k_rows:
        q = compute_quality(
            row["satz"],
            row["typ"],
            row.get("taxonomie", ""),
            verbliste,
        )
        q["qualitaet_label"] = row.get("qualitaet", "").strip()
        q["hochschule"] = row.get("hochschule", "").strip()
        results.append(q)

    # Aggregate
    print("\n" + "=" * 60)
    print("  QUALITÄTSINDIKATOREN (nur K-Sätze)")
    print("=" * 60)

    criteria = [
        ("Q1: Beobachtbares Verb", "q1_verb"),
        ("Q2: Eindeutige Stufe", "q2_eindeutig"),
        ("Q3: Subjekt-Nennung", "q3_subjekt"),
        ("Q4: Spezifisch (>40 Z.)", "q4_spezifisch"),
        ("Q5: Nicht vage", "q5_nicht_vage"),
        ("Q6: Granular (≤2 Verben)", "q6_granular"),
    ]

    print(f"\n{'Kriterium':<30} {'Erfüllt':>8} {'Anteil':>8}")
    print("-" * 50)
    for name, key in criteria:
        count = sum(1 for r in results if r[key])
        pct = count / len(results) * 100
        print(f"{name:<30} {count:>8} {pct:>7.1f}%")

    # Score-Verteilung
    print(f"\n{'Score':<10} {'Anzahl':>8} {'Anteil':>8}")
    print("-" * 30)
    for s in range(7):
        count = sum(1 for r in results if r["score"] == s)
        pct = count / len(results) * 100
        print(f"{s}/6{'':<7} {count:>8} {pct:>7.1f}%")

    avg_score = sum(r["score"] for r in results) / len(results)
    print(f"\nDurchschnittlicher Score: {avg_score:.2f}/6 ({avg_score/6*100:.1f}%)")

    # Korrelation mit manueller Qualitätsbewertung
    print("\n" + "-" * 50)
    print("Korrelation mit manueller Qualitätsbewertung:")
    for label in ["gut", "akzeptabel", "schlecht"]:
        subset = [r for r in results if r["qualitaet_label"] == label]
        if subset:
            avg = sum(r["score"] for r in subset) / len(subset)
            print(f"  {label:<12} n={len(subset):>5}  Ø Score={avg:.2f}/6  ({avg/6*100:.1f}%)")

    # Pro Hochschule
    print("\n" + "-" * 50)
    print("Pro Hochschule:")
    hochschulen = sorted(set(r["hochschule"] for r in results if r["hochschule"]))
    for hs in hochschulen:
        subset = [r for r in results if r["hochschule"] == hs]
        avg = sum(r["score"] for r in subset) / len(subset)
        print(f"  {hs:<30} n={len(subset):>5}  Ø Score={avg:.2f}/6")


if __name__ == "__main__":
    main()
