#!/usr/bin/env python3
"""
Zusammenführung des Gold-Standard-Datensatzes:
1. HS-Fulda-Annotationen v2 (qualifikationsziele_fulda_annotiert_v2.csv)
2. Externe Annotationen (qualifikationsziele_extern_annotiert.csv)
3. Stratifizierter Train/Test-Split (80/20, nach Hochschule + Typ)

Output: data/goldstandard.csv
"""

import csv
import re
from collections import Counter
from pathlib import Path

from sklearn.model_selection import train_test_split

DATA_DIR = Path(__file__).parent.parent / "data"


def load_fulda():
    """Lädt die re-annotierten HS-Fulda-Daten (v2 mit Mehrfach-Taxonomie + Qualität)."""
    rows = []
    with open(DATA_DIR / "qualifikationsziele_fulda_annotiert_v2.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def load_extern():
    """Lädt die extern annotierten Sätze."""
    path = DATA_DIR / "qualifikationsziele_extern_annotiert.csv"
    if not path.exists():
        print(f"WARNUNG: {path} nicht gefunden. Nur HS-Fulda-Daten.")
        return []

    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            # Normalize taxonomie format: ensure semicolon-separated
            tax = r.get("taxonomie", "")
            if tax and ";" not in tax and tax.isdigit():
                pass  # single digit, fine
            r.setdefault("qualitaet", "")
            r.setdefault("split", "")
            rows.append(r)
    return rows


def stratified_split(rows, test_size=0.2, seed=42):
    """Stratifizierter Split nach Hochschule + Typ."""
    # Build stratification key
    for r in rows:
        hs_short = r["hochschule"][:3]  # "Hoc", "TU ", "TH ", "Uni"
        r["_strat"] = f"{hs_short}_{r['typ']}"

    # Count strata
    strat_counts = Counter(r["_strat"] for r in rows)

    # Rows with very rare strata (< 2) can't be split, put in train
    splittable = [r for r in rows if strat_counts[r["_strat"]] >= 2]
    rare = [r for r in rows if strat_counts[r["_strat"]] < 2]

    if splittable:
        strat_labels = [r["_strat"] for r in splittable]
        train_idx, test_idx = train_test_split(
            range(len(splittable)),
            test_size=test_size,
            random_state=seed,
            stratify=strat_labels,
        )
        for i in train_idx:
            splittable[i]["split"] = "train"
        for i in test_idx:
            splittable[i]["split"] = "test"

    for r in rare:
        r["split"] = "train"

    all_rows = splittable + rare

    # Clean up temp key
    for r in all_rows:
        del r["_strat"]

    return all_rows


def main():
    print("Lade HS-Fulda-Annotationen (v2)...")
    existing = load_fulda()
    print(f"  {len(existing)} Sätze")

    print("Lade externe Annotationen...")
    extern = load_extern()
    print(f"  {len(extern)} Sätze")

    # Filter out unannotated
    extern_annotated = [r for r in extern if r.get("typ") and r["typ"] in ("K", "I", "S")]
    unannotated = len(extern) - len(extern_annotated)
    if unannotated > 0:
        print(f"  {unannotated} unannotierte Sätze übersprungen")

    combined = existing + extern_annotated
    print(f"\nKombiniert: {len(combined)} Sätze")

    # Stats
    print("\nVerteilung:")
    for hs in sorted(set(r["hochschule"] for r in combined)):
        hs_rows = [r for r in combined if r["hochschule"] == hs]
        typ_counts = Counter(r["typ"] for r in hs_rows)
        print(f"  {hs}: {len(hs_rows)} Sätze (K={typ_counts.get('K',0)}, I={typ_counts.get('I',0)}, S={typ_counts.get('S',0)})")

    # Stratified split
    print("\nStratifizierter Train/Test-Split (80/20)...")
    combined = stratified_split(combined)

    train = [r for r in combined if r["split"] == "train"]
    test = [r for r in combined if r["split"] == "test"]
    print(f"  Train: {len(train)}, Test: {len(test)}")

    # Verify stratification
    print("\n  Split-Verteilung nach Hochschule:")
    for hs in sorted(set(r["hochschule"] for r in combined)):
        hs_train = sum(1 for r in train if r["hochschule"] == hs)
        hs_test = sum(1 for r in test if r["hochschule"] == hs)
        pct = hs_test / (hs_train + hs_test) * 100 if (hs_train + hs_test) > 0 else 0
        print(f"    {hs}: train={hs_train}, test={hs_test} ({pct:.1f}% test)")

    # Taxonomie distribution in test set
    test_tax = Counter()
    for r in test:
        if r["typ"] == "K" and r["taxonomie"]:
            for t in r["taxonomie"].split(";"):
                if t.strip().isdigit():
                    test_tax[int(t.strip())] += 1
    print("\n  Taxonomiestufen im Test-Set:")
    for stufe in range(1, 7):
        print(f"    Stufe {stufe}: {test_tax.get(stufe, 0)}")

    # Write output
    fieldnames = ["studiengang", "hochschule", "modul_id", "modulname", "satz_nr", "satz",
                  "typ", "taxonomie", "qualitaet", "konfidenz", "split"]

    output_path = DATA_DIR / "goldstandard.csv"
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(combined)

    print(f"\nOutput: {output_path}")
    print(f"Gesamt: {len(combined)} Sätze, {len(set(r['hochschule'] for r in combined))} Hochschulen")


if __name__ == "__main__":
    main()
