"""
Konfidenz-Evaluation: Lädt das Modell manuell über safetensors statt
from_pretrained, um den Segfault in Python 3.14 zu umgehen.
"""
import csv
import os
import sys
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import joblib
import numpy as np
import torch
from safetensors.torch import load_file
from sklearn.metrics import f1_score

DATA_DIR = Path(__file__).parent.parent / "data"
MODELS_DIR = Path(__file__).parent / "backend" / "models"
MODEL_NAME = "T-Systems-onsite/cross-en-de-roberta-sentence-transformer"
SAFETENSORS_PATH = (
    Path.home()
    / ".cache/huggingface/hub/models--T-Systems-onsite--cross-en-de-roberta-sentence-transformer"
    / "snapshots/73fdad86ea7ac68989712ce2007ab43ae89a2ad7/model.safetensors"
)


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )


def encode_sentences(sentences, tokenizer, model, batch_size=64):
    all_embeddings = []
    for i in range(0, len(sentences), batch_size):
        batch = sentences[i : i + batch_size]
        encoded = tokenizer(batch, padding=True, truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            output = model(**encoded)
        embeddings = mean_pooling(output, encoded["attention_mask"])
        all_embeddings.append(embeddings.numpy())
        sys.stderr.write(f"  Batch {i // batch_size + 1}/{(len(sentences) - 1) // batch_size + 1}\n")
    return np.vstack(all_embeddings)


def primary_taxonomy(val):
    if not val or not val.strip():
        return ""
    return val.strip().split(";")[0].strip()


def main():
    clf_type = joblib.load(MODELS_DIR / "svm_type.pkl")
    clf_tax = joblib.load(MODELS_DIR / "svm_taxonomy.pkl")
    print("SVM-Modelle geladen", file=sys.stderr)

    from transformers import AutoTokenizer, AutoConfig
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    print("Tokenizer geladen", file=sys.stderr)

    config = AutoConfig.from_pretrained(MODEL_NAME)
    from transformers.models.xlm_roberta.modeling_xlm_roberta import XLMRobertaModel
    model = XLMRobertaModel(config)
    state_dict = load_file(str(SAFETENSORS_PATH))
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    print("Modell geladen", file=sys.stderr)

    rows = []
    with open(DATA_DIR / "goldstandard.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["split"] == "test":
                r["tax_primary"] = primary_taxonomy(r.get("taxonomie", ""))
                rows.append(r)
    print(f"Test-Set: {len(rows)} Sätze", file=sys.stderr)

    sentences = [r["satz"] for r in rows]
    embeddings = encode_sentences(sentences, tokenizer, model)
    print(f"Embeddings: {embeddings.shape}", file=sys.stderr)

    type_preds = clf_type.predict(embeddings)
    type_proba = clf_type.predict_proba(embeddings)
    type_conf = type_proba.max(axis=1)

    tax_preds = clf_tax.predict(embeddings)
    tax_proba = clf_tax.predict_proba(embeddings)
    tax_conf = tax_proba.max(axis=1)

    y_type_true = [r["typ"].strip() for r in rows]
    y_tax_true = [r["tax_primary"] for r in rows]

    # === TYP-KLASSIFIKATION nach Konfidenz ===
    print("\n" + "=" * 70)
    print("  TYP-KLASSIFIKATION nach Konfidenz-Bins")
    print("=" * 70)

    bins = [("niedrig (<0.5)", 0.0, 0.5), ("mittel (0.5-0.8)", 0.5, 0.8), ("hoch (>=0.8)", 0.8, 1.01)]

    print(f"\n{'Konfidenz':<20} {'n':>6} {'Anteil':>8} {'F1':>8} {'Accuracy':>10}")
    print("-" * 55)
    for name, lo, hi in bins:
        mask = (type_conf >= lo) & (type_conf < hi)
        n = int(mask.sum())
        if n == 0:
            print(f"{name:<20} {0:>6} {'--':>8} {'--':>8} {'--':>10}")
            continue
        pct = n / len(rows) * 100
        true_sub = [y_type_true[i] for i in range(len(rows)) if mask[i]]
        pred_sub = [type_preds[i] for i in range(len(rows)) if mask[i]]
        f1 = f1_score(true_sub, pred_sub, average="weighted", zero_division=0)
        acc = sum(1 for t, p in zip(true_sub, pred_sub) if t == p) / n * 100
        print(f"{name:<20} {n:>6} {pct:>7.1f}% {f1:>8.3f} {acc:>9.1f}%")

    # === TAXONOMIE nach Konfidenz (nur K-Sätze) ===
    print("\n" + "=" * 70)
    print("  TAXONOMIE-ZUORDNUNG nach Konfidenz (nur K-Sätze)")
    print("=" * 70)

    k_mask = np.array([r["typ"].strip() == "K" and r["tax_primary"] != "" for r in rows])

    print(f"\n{'Konfidenz':<20} {'n':>6} {'Anteil':>8} {'F1':>8} {'Accuracy':>10}")
    print("-" * 55)
    for name, lo, hi in bins:
        mask = k_mask & (tax_conf >= lo) & (tax_conf < hi)
        n = int(mask.sum())
        if n == 0:
            print(f"{name:<20} {0:>6} {'--':>8} {'--':>8} {'--':>10}")
            continue
        pct = n / k_mask.sum() * 100
        idx = np.where(mask)[0]
        true_labels = [y_tax_true[i] for i in idx]
        pred_labels = [str(tax_preds[i]) for i in idx]
        f1 = f1_score(true_labels, pred_labels, average="weighted", zero_division=0)
        acc = sum(1 for t, p in zip(true_labels, pred_labels) if t == p) / n * 100
        print(f"{name:<20} {n:>6} {pct:>7.1f}% {f1:>8.3f} {acc:>9.1f}%")

    # === VERGLEICH ===
    print("\n" + "=" * 70)
    print("  VERGLEICH: Alle vs. nur Hoch-Konfidenz (>=0.8)")
    print("=" * 70)

    f1_all_type = f1_score(y_type_true, type_preds, average="weighted")
    high_mask_type = type_conf >= 0.8
    f1_high_type = (
        f1_score(
            [y_type_true[i] for i in range(len(rows)) if high_mask_type[i]],
            [type_preds[i] for i in range(len(rows)) if high_mask_type[i]],
            average="weighted",
        )
        if high_mask_type.sum() > 0
        else 0.0
    )

    k_indices = np.where(k_mask)[0]
    f1_all_tax = f1_score(
        [y_tax_true[i] for i in k_indices],
        [str(tax_preds[i]) for i in k_indices],
        average="weighted",
    )
    high_mask_tax = k_mask & (tax_conf >= 0.8)
    f1_high_tax = (
        f1_score(
            [y_tax_true[i] for i in np.where(high_mask_tax)[0]],
            [str(tax_preds[i]) for i in np.where(high_mask_tax)[0]],
            average="weighted",
        )
        if high_mask_tax.sum() > 0
        else 0.0
    )

    print(f"\n{'Metrik':<25} {'Alle':>10} {'Hoch (>=0.8)':>13} {'Abdeckung':>10}")
    print("-" * 60)
    print(
        f"{'Typ-F1':<25} {f1_all_type:>10.3f} {f1_high_type:>13.3f} {high_mask_type.sum() / len(rows) * 100:>9.1f}%"
    )
    print(
        f"{'Tax-F1':<25} {f1_all_tax:>10.3f} {f1_high_tax:>13.3f} {high_mask_tax.sum() / k_mask.sum() * 100:>9.1f}%"
    )

    print(f"\nØ Typ-Konfidenz:  {type_conf.mean():.3f}")
    print(f"Ø Tax-Konfidenz:  {tax_conf[k_mask].mean():.3f}")

    # Korrekt vs. falsch klassifiziert: Konfidenz-Vergleich
    print("\n" + "=" * 70)
    print("  KONFIDENZ: Korrekt vs. Falsch")
    print("=" * 70)
    correct_type = np.array([y == p for y, p in zip(y_type_true, type_preds)])
    print(f"  Typ korrekt:   Ø Konfidenz = {type_conf[correct_type].mean():.3f} (n={correct_type.sum()})")
    print(f"  Typ falsch:    Ø Konfidenz = {type_conf[~correct_type].mean():.3f} (n={(~correct_type).sum()})")

    correct_tax = np.array([y_tax_true[i] == str(tax_preds[i]) for i in k_indices])
    print(f"  Tax korrekt:   Ø Konfidenz = {tax_conf[k_indices][correct_tax].mean():.3f} (n={correct_tax.sum()})")
    print(f"  Tax falsch:    Ø Konfidenz = {tax_conf[k_indices][~correct_tax].mean():.3f} (n={(~correct_tax).sum()})")

    # Punktbiseriale Korrelation: Konfidenz vs. Korrektheit
    from scipy.stats import pointbiserialr
    print("\n" + "=" * 70)
    print("  KORRELATION: Konfidenz vs. Korrektheit (punktbiserial)")
    print("=" * 70)
    r_type, p_type = pointbiserialr(correct_type.astype(int), type_conf)
    print(f"  Typ:  r = {r_type:.3f}, p = {p_type:.2e}, n = {len(correct_type)}")
    r_tax, p_tax = pointbiserialr(correct_tax.astype(int), tax_conf[k_indices])
    print(f"  Tax:  r = {r_tax:.3f}, p = {p_tax:.2e}, n = {len(correct_tax)}")



if __name__ == "__main__":
    main()
