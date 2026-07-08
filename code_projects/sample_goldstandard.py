#!/usr/bin/env python3
"""
Geschichtetes Sampling für den Gold-Standard.

Strategie:
  - 300 Sätze insgesamt
  - ALLE niedrig-konfidenten Sätze (< 0.7) → ~171
  - ALLE I- und S-Sätze (bis zu einem Cap) → Grenzfälle brauchen Prüfung
  - Rest: proportional nach Taxonomiestufe, aber mit Mindestquoten für seltene Stufen
  - Diversität: maximal 3 Sätze pro Modul, um Breite zu sichern

Output: CSV mit den Stichproben-Sätzen + leere Spalten für manuelle Korrektur.
"""

import csv
import random
from collections import defaultdict
from pathlib import Path

random.seed(42)

TARGET_SIZE = 300

# Minimum samples per taxonomy level
MIN_PER_LEVEL = 15

# Max sentences per module to ensure diversity
MAX_PER_MODULE = 3


def main():
    base_dir = Path(__file__).parent.parent
    input_csv = base_dir / "data" / "qualifikationsziele_annotiert.csv"
    output_csv = base_dir / "data" / "goldstandard_sample.csv"

    with open(input_csv, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for i, r in enumerate(rows):
        r['_idx'] = i

    selected = set()

    # --- Priority 1: All low-confidence sentences ---
    low_conf = [r for r in rows if float(r['konfidenz']) < 0.7]
    for r in low_conf:
        selected.add(r['_idx'])
    print(f"P1: {len(low_conf)} niedrig-konfidente Sätze (alle)")

    # --- Priority 2: All I and S sentences (up to 50) ---
    non_k = [r for r in rows if r['typ'] in ('I', 'S') and r['_idx'] not in selected]
    random.shuffle(non_k)
    non_k_sample = non_k[:50]
    for r in non_k_sample:
        selected.add(r['_idx'])
    print(f"P2: {len(non_k_sample)} I/S-Sätze (von {len(non_k) + len([r for r in low_conf if r['typ'] in ('I','S')])} total)")

    # --- Priority 3: Ensure minimum per taxonomy level ---
    k_rows = [r for r in rows if r['typ'] == 'K']
    by_level = defaultdict(list)
    for r in k_rows:
        by_level[r['taxonomie']].append(r)

    for level in '123456':
        already = [r for r in rows if r['_idx'] in selected and r.get('taxonomie') == level]
        needed = max(0, MIN_PER_LEVEL - len(already))
        if needed > 0:
            candidates = [r for r in by_level[level] if r['_idx'] not in selected]
            random.shuffle(candidates)
            for r in candidates[:needed]:
                selected.add(r['_idx'])
    print(f"P3: Minimum {MIN_PER_LEVEL}/Stufe sichergestellt → jetzt {len(selected)} Sätze")

    # --- Priority 4: Fill remaining slots proportionally ---
    remaining = TARGET_SIZE - len(selected)
    if remaining > 0:
        # Track module usage
        module_count = defaultdict(int)
        for idx in selected:
            r = rows[idx]
            module_count[r['modul_id']] += 1

        # Candidates: K sentences not yet selected, respecting max per module
        candidates = []
        for r in k_rows:
            if r['_idx'] not in selected and module_count[r['modul_id']] < MAX_PER_MODULE:
                candidates.append(r)

        # Stratified by taxonomy level (proportional)
        level_counts = defaultdict(int)
        for r in candidates:
            level_counts[r['taxonomie']] += 1

        total_candidates = sum(level_counts.values())
        level_quotas = {}
        for level in '123456':
            level_quotas[level] = max(1, round(remaining * level_counts[level] / total_candidates))

        # Adjust to hit target
        total_quota = sum(level_quotas.values())
        if total_quota > remaining:
            # Reduce largest bucket
            largest = max(level_quotas, key=level_quotas.get)
            level_quotas[largest] -= (total_quota - remaining)

        by_level_cand = defaultdict(list)
        for r in candidates:
            by_level_cand[r['taxonomie']].append(r)

        for level in '123456':
            pool = by_level_cand[level]
            # Prefer medium confidence (more interesting for validation)
            pool.sort(key=lambda r: abs(float(r['konfidenz']) - 0.75))
            for r in pool[:level_quotas.get(level, 0)]:
                selected.add(r['_idx'])
                module_count[r['modul_id']] += 1

    print(f"P4: Proportional aufgefüllt → {len(selected)} Sätze")

    # --- Build output ---
    sample = [rows[idx] for idx in sorted(selected)]

    # Statistics
    print(f"\n{'='*50}")
    print(f"STICHPROBE: {len(sample)} Sätze\n")

    typ_counts = defaultdict(int)
    tax_counts = defaultdict(int)
    conf_buckets = {'niedrig': 0, 'mittel': 0, 'hoch': 0}
    sg_counts = defaultdict(int)

    for r in sample:
        typ_counts[r['typ']] += 1
        if r['typ'] == 'K':
            tax_counts[r['taxonomie']] += 1
        c = float(r['konfidenz'])
        if c < 0.7:
            conf_buckets['niedrig'] += 1
        elif c < 0.85:
            conf_buckets['mittel'] += 1
        else:
            conf_buckets['hoch'] += 1
        sg_counts[r['studiengang']] += 1

    print("Typ-Verteilung:")
    for t in ['K', 'I', 'S']:
        print(f"  {t}: {typ_counts[t]}")

    print("\nTaxonomie (K-Sätze):")
    labels = {'1': 'Erinnern', '2': 'Verstehen', '3': 'Anwenden',
              '4': 'Analysieren', '5': 'Bewerten', '6': 'Erschaffen'}
    for level in '123456':
        print(f"  {level} {labels[level]:12s}: {tax_counts[level]}")

    print(f"\nKonfidenz: niedrig={conf_buckets['niedrig']}, "
          f"mittel={conf_buckets['mittel']}, hoch={conf_buckets['hoch']}")

    print(f"\nStudiengänge vertreten: {len(sg_counts)}/15")

    # Write output
    fieldnames = [
        "studiengang", "modul_id", "modulname", "satz_nr", "satz",
        "llm_typ", "llm_taxonomie", "llm_konfidenz",
        "typ", "taxonomie", "kommentar"
    ]

    out_rows = []
    for r in sample:
        out_rows.append({
            "studiengang": r['studiengang'],
            "modul_id": r['modul_id'],
            "modulname": r['modulname'],
            "satz_nr": r['satz_nr'],
            "satz": r['satz'],
            "llm_typ": r['typ'],
            "llm_taxonomie": r['taxonomie'],
            "llm_konfidenz": r['konfidenz'],
            "typ": "",
            "taxonomie": "",
            "kommentar": "",
        })

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"\nOutput: {output_csv}")
    print("Spalten 'typ', 'taxonomie', 'kommentar' sind leer → für manuelle Annotation")


if __name__ == "__main__":
    main()
