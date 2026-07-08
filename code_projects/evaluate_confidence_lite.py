"""
Leichtgewichtige Konfidenz-Evaluation: Nutzt vorberechnete Embeddings
statt das SBERT-Modell neu zu laden.
"""
import csv
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import f1_score

sys.path.insert(0, str(Path(__file__).parent / "backend"))

DATA_DIR = Path(__file__).parent.parent / "data"
MODELS_DIR = Path(__file__).parent / "backend" / "models"


def primary_taxonomy(val):
    if not val or not val.strip():
        return ""
    return val.strip().split(";")[0].strip()


def main():
    # Lade Klassifikatoren
    clf_type = joblib.load(MODELS_DIR / "svm_type.pkl")
    clf_tax = joblib.load(MODELS_DIR / "svm_taxonomy.pkl")
    print("SVM-Modelle geladen")

    # Lade SBERT-Modell für Embeddings
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("T-Systems-onsite/cross-en-de-roberta-sentence-transformer")
    print("SBERT geladen")

    # Lade Test-Set
    rows = []
    with open(DATA_DIR / "goldstandard.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["split"] == "test":
                r["tax_primary"] = primary_taxonomy(r.get("taxonomie", ""))
                rows.append(r)
    print(f"Test-Set: {len(rows)} Sätze")

    # Batch-Encode
    sentences = [r["satz"] for r in rows]
    embeddings = model.encode(sentences, batch_size=64, show_progress_bar=True)
    print(f"Embeddings berechnet: {embeddings.shape}")

    # Klassifiziere
    type_preds = clf_type.predict(embeddings)
    type_proba = clf_type.predict_proba(embeddings)
    type_conf = type_proba.max(axis=1)

    tax_preds = clf_tax.predict(embeddings)
    tax_proba = clf_tax.predict_proba(embeddings)
    tax_conf = tax_proba.max(axis=1)

    # Kombinierte Konfidenz (wie in pipeline.py)
    combined_conf = np.minimum(type_conf, tax_conf)

    # Ground truth
    y_type_true = [r["typ"].strip() for r in rows]
    y_tax_true = [r["tax_primary"] for r in rows]

    # === TYP-KLASSIFIKATION nach Konfidenz ===
    print("\n" + "=" * 70)
    print("  TYP-KLASSIFIKATION nach Konfidenz")
    print("=" * 70)

    bins = [("niedrig", 0.0, 0.5), ("mittel", 0.5, 0.8), ("hoch", 0.8, 1.01)]

    print(f"\n{'Konfidenz':<15} {'n':>6} {'Anteil':>8} {'F1':>8} {'Accuracy':>10}")
    print("-" * 50)
    for name, lo, hi in bins:
        mask = (type_conf >= lo) & (type_conf < hi)
        n = mask.sum()
        if n == 0:
            print(f"{name:<15} {0:>6} {'--':>8} {'--':>8} {'--':>10}")
            continue
        pct = n / len(rows) * 100
        f1 = f1_score([y_type_true[i] for i in range(len(rows)) if mask[i]],
                      [type_preds[i] for i in range(len(rows)) if mask[i]],
                      average="weighted")
        acc = sum(1 for i in range(len(rows)) if mask[i] and y_type_true[i] == type_preds[i]) / n
        print(f"{name:<15} {n:>6} {pct:>7.1f}% {f1:>8.3f} {acc:>9.1f}%")

    # === TAXONOMIE nach Konfidenz (nur K-Sätze) ===
    print("\n" + "=" * 70)
    print("  TAXONOMIE-ZUORDNUNG nach Konfidenz (nur K-Sätze)")
    print("=" * 70)

    k_mask = np.array([r["typ"].strip() == "K" and r["tax_primary"] != "" for r in rows])
    k_indices = np.where(k_mask)[0]

    print(f"\n{'Konfidenz':<15} {'n':>6} {'Anteil':>8} {'F1':>8} {'Accuracy':>10}")
    print("-" * 50)
    for name, lo, hi in bins:
        mask = k_mask & (tax_conf >= lo) & (tax_conf < hi)
        n = mask.sum()
        if n == 0:
            print(f"{name:<15} {0:>6} {'--':>8} {'--':>8} {'--':>10}")
            continue
        pct = n / k_mask.sum() * 100
        idx = np.where(mask)[0]
        true_labels = [y_tax_true[i] for i in idx]
        pred_labels = [str(tax_preds[i]) for i in idx]
        f1 = f1_score(true_labels, pred_labels, average="weighted")
        acc = sum(1 for t, p in zip(true_labels, pred_labels) if t == p) / n
        print(f"{name:<15} {n:>6} {pct:>7.1f}% {f1:>8.3f} {acc:>9.1f}%")

    # === Gesamt (nur Hoch-Konfidenz) ===
    print("\n" + "=" * 70)
    print("  VERGLEICH: Alle vs. nur Hoch-Konfidenz")
    print("=" * 70)

    f1_all_type = f1_score(y_type_true, type_preds, average="weighted")
    high_mask_type = type_conf >= 0.8
    if high_mask_type.sum() > 0:
        f1_high_type = f1_score(
            [y_type_true[i] for i in range(len(rows)) if high_mask_type[i]],
            [type_preds[i] for i in range(len(rows)) if high_mask_type[i]],
            average="weighted")
    else:
        f1_high_type = 0.0

    f1_all_tax = f1_score(
        [y_tax_true[i] for i in k_indices],
        [str(tax_preds[i]) for i in k_indices],
        average="weighted")
    high_mask_tax = k_mask & (tax_conf >= 0.8)
    if high_mask_tax.sum() > 0:
        idx_high = np.where(high_mask_tax)[0]
        f1_high_tax = f1_score(
            [y_tax_true[i] for i in idx_high],
            [str(tax_preds[i]) for i in idx_high],
            average="weighted")
    else:
        f1_high_tax = 0.0

    print(f"\n{'Metrik':<25} {'Alle':>10} {'Hoch (>0.8)':>12} {'Abdeckung':>10}")
    print("-" * 60)
    print(f"{'Typ-F1':<25} {f1_all_type:>10.3f} {f1_high_type:>12.3f} {high_mask_type.sum()/len(rows)*100:>9.1f}%")
    print(f"{'Tax-F1':<25} {f1_all_tax:>10.3f} {f1_high_tax:>12.3f} {high_mask_tax.sum()/k_mask.sum()*100:>9.1f}%")

    # Ø Konfidenz
    print(f"\nØ Typ-Konfidenz:  {type_conf.mean():.3f}")
    print(f"Ø Tax-Konfidenz:  {tax_conf[k_mask].mean():.3f}")


if __name__ == "__main__":
    main()
