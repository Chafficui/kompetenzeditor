#!/usr/bin/env python3
"""
Evaluierung von Sentence-Embedding-Modellen für die Kompetenzformulierungs-Analyse.

Testet Kandidaten-Modelle auf zwei Aufgaben:
  1. Klassifikation: K vs. I vs. S (Satztyp)
  2. Taxonomie: Stufe 1–6 (nur K-Sätze)

Methode:
  - Sätze mit jedem Modell embedden
  - SVM-Klassifikator auf Train-Split trainieren
  - Auf Test-Split evaluieren (Precision, Recall, F1)
  - Zusätzlich: Intra-/Inter-Klassen-Ähnlichkeit messen

Nutzung:
  python3 evaluate_embeddings.py
"""

import csv
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

MODELS = [
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "deutsche-telekom/gbert-large-paraphrase-cosine",
    "T-Systems-onsite/cross-en-de-roberta-sentence-transformer",
]

BASE_DIR = Path(__file__).parent.parent
DATA_CSV = BASE_DIR / "data" / "qualifikationsziele_annotiert.csv"


def load_data():
    with open(DATA_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    train, test = [], []
    for r in rows:
        entry = {
            "satz": r["satz"],
            "typ": r["typ"],
            "taxonomie": r["taxonomie"],
        }
        if r["split"] == "train":
            train.append(entry)
        else:
            test.append(entry)

    return train, test


def compute_similarity_stats(embeddings, labels):
    """Mittlere Cosine-Similarity innerhalb und zwischen Klassen."""
    from numpy.linalg import norm

    label_set = sorted(set(labels))
    label_to_idx = defaultdict(list)
    for i, l in enumerate(labels):
        label_to_idx[l].append(i)

    intra = {}
    for label in label_set:
        idxs = label_to_idx[label]
        if len(idxs) < 2:
            intra[label] = float("nan")
            continue
        vecs = embeddings[idxs]
        norms = vecs / (norm(vecs, axis=1, keepdims=True) + 1e-10)
        sim_matrix = norms @ norms.T
        n = len(idxs)
        # Obere Dreiecksmatrix ohne Diagonale
        mask = np.triu(np.ones((n, n), dtype=bool), k=1)
        intra[label] = float(sim_matrix[mask].mean())

    # Inter-Klassen: je zwei Klassen
    inter_pairs = {}
    for i, l1 in enumerate(label_set):
        for l2 in label_set[i + 1:]:
            v1 = embeddings[label_to_idx[l1]]
            v2 = embeddings[label_to_idx[l2]]
            n1 = v1 / (norm(v1, axis=1, keepdims=True) + 1e-10)
            n2 = v2 / (norm(v2, axis=1, keepdims=True) + 1e-10)
            sim = (n1 @ n2.T).mean()
            inter_pairs[f"{l1}↔{l2}"] = float(sim)

    return intra, inter_pairs


def evaluate_model(model_name, train_data, test_data):
    print(f"\n{'='*70}")
    print(f"Modell: {model_name}")
    print(f"{'='*70}")

    t0 = time.time()
    model = SentenceTransformer(model_name)
    load_time = time.time() - t0
    print(f"Ladezeit: {load_time:.1f}s")

    dim = model.get_sentence_embedding_dimension()
    print(f"Embedding-Dimension: {dim}")

    train_sents = [d["satz"] for d in train_data]
    test_sents = [d["satz"] for d in test_data]

    t0 = time.time()
    train_emb = model.encode(train_sents, show_progress_bar=True, batch_size=64)
    encode_train_time = time.time() - t0

    t0 = time.time()
    test_emb = model.encode(test_sents, show_progress_bar=True, batch_size=64)
    encode_test_time = time.time() - t0

    total_sents = len(train_sents) + len(test_sents)
    total_time = encode_train_time + encode_test_time
    print(f"Encoding: {total_sents} Sätze in {total_time:.1f}s "
          f"({total_sents/total_time:.0f} Sätze/s)")

    results = {"model": model_name, "dim": dim, "encode_speed": total_sents / total_time}

    # --- Aufgabe 1: Typ-Klassifikation (K/I/S) ---
    print(f"\n--- Aufgabe 1: Typ-Klassifikation (K/I/S) ---")
    train_labels_typ = [d["typ"] for d in train_data]
    test_labels_typ = [d["typ"] for d in test_data]

    clf_typ = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=10, gamma="scale"))
    clf_typ.fit(train_emb, train_labels_typ)
    pred_typ = clf_typ.predict(test_emb)

    print(classification_report(test_labels_typ, pred_typ, digits=3, zero_division=0))

    # Similarity-Analyse für Typen
    all_emb_typ = np.vstack([train_emb, test_emb])
    all_labels_typ = train_labels_typ + test_labels_typ
    intra_typ, inter_typ = compute_similarity_stats(all_emb_typ, all_labels_typ)
    print("Intra-Klassen-Ähnlichkeit (Typ):")
    for label, sim in sorted(intra_typ.items()):
        print(f"  {label}: {sim:.3f}")
    print("Inter-Klassen-Ähnlichkeit (Typ):")
    for pair, sim in sorted(inter_typ.items()):
        print(f"  {pair}: {sim:.3f}")

    results["typ_report"] = classification_report(test_labels_typ, pred_typ,
                                                   digits=3, output_dict=True, zero_division=0)

    # --- Aufgabe 2: Taxonomie-Klassifikation (nur K-Sätze) ---
    print(f"\n--- Aufgabe 2: Taxonomie-Klassifikation (Stufe 1–6, nur K-Sätze) ---")

    train_k_mask = [i for i, d in enumerate(train_data) if d["typ"] == "K" and d["taxonomie"]]
    test_k_mask = [i for i, d in enumerate(test_data) if d["typ"] == "K" and d["taxonomie"]]

    train_emb_k = train_emb[train_k_mask]
    test_emb_k = test_emb[test_k_mask]
    train_labels_tax = [train_data[i]["taxonomie"] for i in train_k_mask]
    test_labels_tax = [test_data[i]["taxonomie"] for i in test_k_mask]

    clf_tax = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=10, gamma="scale"))
    clf_tax.fit(train_emb_k, train_labels_tax)
    pred_tax = clf_tax.predict(test_emb_k)

    labels_order = ["1", "2", "3", "4", "5", "6"]
    print(classification_report(test_labels_tax, pred_tax, labels=labels_order,
                                target_names=["Erinnern", "Verstehen", "Anwenden",
                                              "Analysieren", "Bewerten", "Erschaffen"],
                                digits=3, zero_division=0))

    print("Confusion Matrix (Taxonomie):")
    cm = confusion_matrix(test_labels_tax, pred_tax, labels=labels_order)
    header = "      " + "  ".join(f"{l:>4s}" for l in labels_order)
    print(header)
    for i, row in enumerate(cm):
        print(f"  {labels_order[i]}:  " + "  ".join(f"{v:4d}" for v in row))

    # Similarity-Analyse für Taxonomie
    all_k_emb = np.vstack([train_emb_k, test_emb_k])
    all_k_labels = train_labels_tax + test_labels_tax
    intra_tax, inter_tax = compute_similarity_stats(all_k_emb, all_k_labels)
    print("\nIntra-Klassen-Ähnlichkeit (Taxonomie):")
    for label, sim in sorted(intra_tax.items()):
        name = ["", "Erinnern", "Verstehen", "Anwenden", "Analysieren", "Bewerten", "Erschaffen"][int(label)]
        print(f"  {label} {name}: {sim:.3f}")
    print("Inter-Klassen-Ähnlichkeit (benachbarte Stufen):")
    for pair, sim in sorted(inter_tax.items()):
        print(f"  {pair}: {sim:.3f}")

    results["tax_report"] = classification_report(test_labels_tax, pred_tax,
                                                   labels=labels_order, digits=3,
                                                   output_dict=True, zero_division=0)

    del model
    return results


def main():
    train_data, test_data = load_data()
    print(f"Daten geladen: {len(train_data)} Train, {len(test_data)} Test")

    train_k = sum(1 for d in train_data if d["typ"] == "K")
    test_k = sum(1 for d in test_data if d["typ"] == "K")
    print(f"Davon K-Sätze: {train_k} Train, {test_k} Test")

    all_results = []
    for model_name in MODELS:
        try:
            result = evaluate_model(model_name, train_data, test_data)
            all_results.append(result)
        except Exception as e:
            print(f"\nFEHLER bei {model_name}: {e}")
            import traceback
            traceback.print_exc()

    # --- Vergleichstabelle ---
    print(f"\n\n{'='*70}")
    print("VERGLEICH")
    print(f"{'='*70}")

    print(f"\n{'Modell':<55s} {'Dim':>4s} {'Sätze/s':>8s} "
          f"{'Typ-F1':>7s} {'Tax-F1':>7s}")
    print("-" * 85)
    for r in all_results:
        name = r["model"].split("/")[-1][:50]
        typ_f1 = r["typ_report"]["weighted avg"]["f1-score"]
        tax_f1 = r["tax_report"]["weighted avg"]["f1-score"]
        print(f"{name:<55s} {r['dim']:>4d} {r['encode_speed']:>7.0f} "
              f"{typ_f1:>7.3f} {tax_f1:>7.3f}")

    best_tax = max(all_results, key=lambda r: r["tax_report"]["weighted avg"]["f1-score"])
    print(f"\nBestes Modell (Taxonomie): {best_tax['model']}")
    print(f"  Weighted F1: {best_tax['tax_report']['weighted avg']['f1-score']:.3f}")


if __name__ == "__main__":
    main()
