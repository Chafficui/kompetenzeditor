"""
Precision@k ohne Test-Set-Leakage: Referenz-DB auf Trainings-Sätze beschränkt.

Vergleicht Precision@{1,3,5} der SBERT-Ähnlichkeitssuche in zwei Settings:
  (a) volle Referenz-DB (wie in der Thesis berichtet, enthält Test-Sätze)
  (b) Trainings-only-Referenz-DB (kein Leakage)

Nutzt den safetensors-Ladepfad aus evaluate_confidence_raw.py (Python-3.14-Workaround).
"""
import csv
import os
import sys
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import json
import numpy as np
import torch
from safetensors.torch import load_file

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


def precision_at_k(test_rows, test_emb, ref_emb, ref_meta, k):
    """ref_emb ist zeilennormalisiert; test_emb wird hier normalisiert."""
    ref_tax = np.array([primary_taxonomy(str(m["taxonomie"])) for m in ref_meta])
    ref_typ = np.array([m["typ"] for m in ref_meta])
    ref_satz = np.array([m["satz"] for m in ref_meta])
    typ_mask = ref_typ == "K"

    psum, count = 0.0, 0
    for i, r in enumerate(test_rows):
        q = test_emb[i]
        q = q / (np.linalg.norm(q) + 1e-10)
        sims = ref_emb @ q
        mask = typ_mask & (ref_satz != r["satz"])
        idx = np.where(mask)[0]
        if len(idx) == 0:
            continue
        top = idx[np.argsort(sims[idx])[::-1][:k]]
        relevant = int(np.sum(ref_tax[top] == r["tax_primary"]))
        psum += relevant / len(top)
        count += 1
    return psum / count if count else 0.0


def main():
    # Daten
    train_texts = set()
    test_k = []
    with open(DATA_DIR / "goldstandard.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["split"] == "train":
                train_texts.add(r["satz"])
            elif r["split"] == "test":
                tp = primary_taxonomy(r.get("taxonomie", ""))
                if r["typ"].strip() == "K" and tp:
                    test_k.append({"satz": r["satz"], "tax_primary": tp})
    print(f"Test-K-Sätze mit Primärstufe: {len(test_k)}", file=sys.stderr)

    # Referenz-DB
    ref_emb = np.load(MODELS_DIR / "reference_embeddings.npy")
    with open(MODELS_DIR / "reference_metadata.json", encoding="utf-8") as f:
        ref_meta = json.load(f)
    assert len(ref_meta) == ref_emb.shape[0]
    print(f"Referenz-DB: {len(ref_meta)} Sätze", file=sys.stderr)

    train_mask = np.array([m["satz"] in train_texts for m in ref_meta])
    ref_emb_train = ref_emb[train_mask]
    ref_meta_train = [m for m, keep in zip(ref_meta, train_mask) if keep]
    print(f"Trainings-only-Referenz: {len(ref_meta_train)} Sätze "
          f"({int((~train_mask).sum())} Test-/Restsätze entfernt)", file=sys.stderr)

    # Test-Embeddings
    from transformers import AutoTokenizer, AutoConfig
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    config = AutoConfig.from_pretrained(MODEL_NAME)
    from transformers.models.xlm_roberta.modeling_xlm_roberta import XLMRobertaModel
    model = XLMRobertaModel(config)
    model.load_state_dict(load_file(str(SAFETENSORS_PATH)), strict=False)
    model.eval()
    print("Modell geladen", file=sys.stderr)

    test_emb = encode_sentences([r["satz"] for r in test_k], tokenizer, model)

    print("\n" + "=" * 60)
    print("  PRECISION@K: voll vs. trainings-only Referenz-DB")
    print("=" * 60)
    print(f"{'k':>3} {'voll (Thesis)':>15} {'trainings-only':>16}")
    for k in [1, 3, 5]:
        p_full = precision_at_k(test_k, test_emb, ref_emb, ref_meta, k)
        p_clean = precision_at_k(test_k, test_emb, ref_emb_train, ref_meta_train, k)
        print(f"{k:>3} {p_full:>15.3f} {p_clean:>16.3f}")


if __name__ == "__main__":
    main()
