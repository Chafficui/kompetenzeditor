#!/usr/bin/env python3
"""
Zieht eine stratifizierte Stichprobe aus dem Gold-Standard für die manuelle Validierung.
Stratifiziert nach: Hochschule, Taxonomiestufe, LLM-Konfidenz.

Output:
  - data/validierungsstichprobe.csv (300 Sätze zur manuellen Prüfung)
  - Spalten: alle Gold-Standard-Spalten + val_typ, val_taxonomie, val_qualitaet (für manuelles Eintragen)
"""

import csv
import random
from collections import Counter, defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
SAMPLE_SIZE = 300
SEED = 42


def main():
    # Load gold standard
    input_path = DATA_DIR / "goldstandard.csv"
    if not input_path.exists():
        print(f"FEHLER: {input_path} nicht gefunden. Erst merge_goldstandard.py ausführen.")
        return

    with open(input_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Gold-Standard: {len(rows)} Sätze")

    # Build stratification groups
    groups = defaultdict(list)
    for i, r in enumerate(rows):
        hs = r["hochschule"]
        typ = r["typ"]
        # Confidence bucket: low (<0.7), medium (0.7-0.9), high (>0.9)
        try:
            conf = float(r.get("konfidenz", 0.8))
        except ValueError:
            conf = 0.8
        conf_bucket = "low" if conf < 0.7 else ("medium" if conf < 0.9 else "high")

        key = f"{hs}|{typ}|{conf_bucket}"
        groups[key].append(i)

    print(f"\n{len(groups)} Stratifikationsgruppen:")
    for key in sorted(groups.keys()):
        print(f"  {key}: {len(groups[key])}")

    # Proportional sampling
    random.seed(SEED)
    total = len(rows)
    sampled_indices = set()

    for key, indices in groups.items():
        # Proportional allocation
        n_sample = max(1, round(len(indices) / total * SAMPLE_SIZE))
        # Ensure we don't sample more than available
        n_sample = min(n_sample, len(indices))
        selected = random.sample(indices, n_sample)
        sampled_indices.update(selected)

    # If we have too few, add random extras
    remaining = list(set(range(total)) - sampled_indices)
    while len(sampled_indices) < SAMPLE_SIZE and remaining:
        idx = random.choice(remaining)
        remaining.remove(idx)
        sampled_indices.add(idx)

    # If we have too many, trim
    sampled_indices = list(sampled_indices)
    if len(sampled_indices) > SAMPLE_SIZE:
        random.shuffle(sampled_indices)
        sampled_indices = sampled_indices[:SAMPLE_SIZE]

    sample = [rows[i] for i in sorted(sampled_indices)]
    print(f"\nStichprobe: {len(sample)} Sätze")

    # Stats
    print("\nVerteilung in Stichprobe:")
    for hs in sorted(set(r["hochschule"] for r in sample)):
        hs_count = sum(1 for r in sample if r["hochschule"] == hs)
        hs_total = sum(1 for r in rows if r["hochschule"] == hs)
        print(f"  {hs}: {hs_count} ({hs_count/len(sample)*100:.1f}%, Datensatz: {hs_total/len(rows)*100:.1f}%)")

    print("\nTyp-Verteilung:")
    for typ in ["K", "I", "S"]:
        count = sum(1 for r in sample if r["typ"] == typ)
        total_count = sum(1 for r in rows if r["typ"] == typ)
        print(f"  {typ}: {count} ({count/len(sample)*100:.1f}%, Datensatz: {total_count/len(rows)*100:.1f}%)")

    # Add validation columns
    output_path = DATA_DIR / "validierungsstichprobe.csv"
    fieldnames = list(sample[0].keys()) + ["val_typ", "val_taxonomie", "val_qualitaet", "val_kommentar"]

    for r in sample:
        r["val_typ"] = ""
        r["val_taxonomie"] = ""
        r["val_qualitaet"] = ""
        r["val_kommentar"] = ""

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample)

    print(f"\nOutput: {output_path}")
    print(f"→ Die val_*-Spalten sind leer und müssen manuell ausgefüllt werden.")
    print(f"→ Danach kann Cohen's Kappa berechnet werden (LLM vs. manuell).")


if __name__ == "__main__":
    main()
