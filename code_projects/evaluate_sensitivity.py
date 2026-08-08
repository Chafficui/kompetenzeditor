"""
Sensitivitätsanalyse: Kernmetriken ausschließlich auf den manuell validierten
Sätzen der Validierungsstichprobe, mit den MENSCHLICHEN Labels (Erstannotator)
als Ground Truth statt der LLM-Labels des Gold-Standards.

Prüft, ob die Rangfolge der drei Ansätze (Regel / Embedding / Hybrid) auch dann
bestehen bleibt, wenn die Referenz nicht vom LLM stammt — Entkräftung des
Zirkularitätsarguments (SBERT+SVM reproduziert nur LLM-Urteile).

Berichtet: (a) alle gematchten validierten Sätze, (b) nur die im Test-Split
(vom SVM-Training unberührt).
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from evaluate_approaches import (
    evaluate_rule_based,
    evaluate_embedding,
    evaluate_hybrid,
    primary_taxonomy,
)
from sklearn.metrics import f1_score
import spacy
from rule_based import RuleBasedAnalyzer
from embedding_service import EmbeddingService

DATA_DIR = Path(__file__).parent.parent / "data"


def norm(s):
    s = re.sub(r"\s*\[cite:[^\]]*\]", "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def build_rows():
    gs = {}
    with open(DATA_DIR / "goldstandard.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            gs.setdefault(norm(r["satz"]), r)

    rows = []
    with open(DATA_DIR / "validierung_annotiert_erstannotator.csv", encoding="utf-8") as f:
        for v in csv.DictReader(f):
            g = gs.get(norm(v["satz"]))
            if not g:
                continue
            rows.append({
                "satz": g["satz"],  # Gold-Standard-Fassung (ohne cite-Artefakte)
                "typ": v["val_typ"].strip(),                      # menschliches Label
                "taxonomie_primary": primary_taxonomy(v.get("val_taxonomie", "")),
                "split": g["split"],
            })
    return rows


def report(name, rows, nlp, analyzer, emb):
    print(f"\n=== {name} (n={len(rows)}) ===")
    results = {}
    r_tt, r_pt, r_ta, r_pa = evaluate_rule_based(rows, nlp, analyzer)
    e_tt, e_pt, e_ta, e_pa = evaluate_embedding(rows, emb)
    h_tt, h_pt, h_ta, h_pa, _ = evaluate_hybrid(rows, nlp, analyzer, emb)
    for label, (tt, pt, ta, pa) in [
        ("Regel", (r_tt, r_pt, r_ta, r_pa)),
        ("Embedding", (e_tt, e_pt, e_ta, e_pa)),
        ("Hybrid", (h_tt, h_pt, h_ta, h_pa)),
    ]:
        f1_typ = f1_score(tt, pt, average="weighted")
        # Taxonomie: nur Sätze mit menschlicher K+Stufe; "0" = keine Zuordnung
        f1_tax = f1_score(ta, pa, average="weighted") if ta else float("nan")
        cov = sum(1 for p in pa if p != "0") / len(pa) * 100 if pa else 0
        print(f"  {label:<10} Typ-F1={f1_typ:.3f}  Tax-F1={f1_tax:.3f} (Abdeckung {cov:.1f}%, n_tax={len(ta)})")
        results[label] = (f1_typ, f1_tax)
    return results


def main():
    rows = build_rows()
    test_rows = [r for r in rows if r["split"] == "test"]
    print(f"Validierte Sätze gematcht: {len(rows)}, davon Test-Split: {len(test_rows)}")

    print("Lade Modelle...", file=sys.stderr)
    nlp = spacy.load("de_core_news_lg")
    analyzer = RuleBasedAnalyzer()
    emb = EmbeddingService()
    emb.load()

    report("Alle validierten Sätze (menschliche Labels)", rows, nlp, analyzer, emb)
    report("Nur Test-Split (menschliche Labels)", test_rows, nlp, analyzer, emb)


if __name__ == "__main__":
    main()
