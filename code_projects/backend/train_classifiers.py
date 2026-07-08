#!/usr/bin/env python3
"""
Trainiert SVM-Klassifikatoren für Typ (K/I/S) und Taxonomie (1-6).

Verwendet den Gold-Standard-Datensatz (5617 Sätze, 4 Hochschulen)
und das T-Systems SBERT-Modell. Taxonomie wird auf Primärstufe
reduziert (erster Wert bei Mehrfachzuordnung).

Nutzung:
    python train_classifiers.py
"""

import csv
import time
from pathlib import Path

import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics import classification_report
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

MODEL_NAME = "T-Systems-onsite/cross-en-de-roberta-sentence-transformer"
BASE_DIR = Path(__file__).parent
DATA_CSV = BASE_DIR.parent.parent / "data" / "goldstandard.csv"
MODELS_DIR = BASE_DIR / "models"


def primary_taxonomy(val):
    """Extrahiert die Primärstufe (erste Stufe bei Mehrfachzuordnung)."""
    if not val or not val.strip():
        return ""
    return val.strip().split(";")[0].strip()


def load_data():
    with open(DATA_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    train, test = [], []
    for r in rows:
        entry = {
            "satz": r["satz"],
            "typ": r["typ"],
            "taxonomie": primary_taxonomy(r.get("taxonomie", "")),
            "hochschule": r.get("hochschule", ""),
        }
        if r["split"] == "train":
            train.append(entry)
        else:
            test.append(entry)

    return train, test


def main():
    MODELS_DIR.mkdir(exist_ok=True)

    print("Lade Daten...")
    train_data, test_data = load_data()
    print(f"  Train: {len(train_data)}, Test: {len(test_data)}")

    print(f"\nLade SBERT-Modell: {MODEL_NAME}")
    t0 = time.time()
    model = SentenceTransformer(MODEL_NAME)
    print(f"  Geladen in {time.time() - t0:.1f}s")

    print("\nBerechne Embeddings...")
    train_sents = [d["satz"] for d in train_data]
    test_sents = [d["satz"] for d in test_data]

    t0 = time.time()
    train_emb = model.encode(train_sents, show_progress_bar=True, batch_size=64)
    test_emb = model.encode(test_sents, show_progress_bar=True, batch_size=64)
    print(f"  {len(train_sents) + len(test_sents)} Sätze in {time.time() - t0:.1f}s")

    # --- SVM Typ-Klassifikation (K/I/S) ---
    print("\n--- Trainiere SVM-Type (K/I/S) ---")
    train_labels_typ = [d["typ"] for d in train_data]
    test_labels_typ = [d["typ"] for d in test_data]

    clf_typ = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=10, gamma="scale", probability=True))
    clf_typ.fit(train_emb, train_labels_typ)

    pred_typ = clf_typ.predict(test_emb)
    print(classification_report(test_labels_typ, pred_typ, digits=3, zero_division=0))

    typ_path = MODELS_DIR / "svm_type.pkl"
    joblib.dump(clf_typ, typ_path)
    print(f"  Gespeichert: {typ_path}")

    # --- SVM Taxonomie-Klassifikation (Stufe 1-6, nur K) ---
    print("\n--- Trainiere SVM-Taxonomy (Stufe 1-6, nur K-Sätze, Primärstufe) ---")
    train_k_idx = [i for i, d in enumerate(train_data) if d["typ"] == "K" and d["taxonomie"]]
    test_k_idx = [i for i, d in enumerate(test_data) if d["typ"] == "K" and d["taxonomie"]]

    train_emb_k = train_emb[train_k_idx]
    test_emb_k = test_emb[test_k_idx]
    train_labels_tax = [train_data[i]["taxonomie"] for i in train_k_idx]
    test_labels_tax = [test_data[i]["taxonomie"] for i in test_k_idx]

    print(f"  Train K-Sätze mit Taxonomie: {len(train_k_idx)}")
    print(f"  Test K-Sätze mit Taxonomie: {len(test_k_idx)}")

    clf_tax = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=10, gamma="scale", probability=True))
    clf_tax.fit(train_emb_k, train_labels_tax)

    pred_tax = clf_tax.predict(test_emb_k)
    labels_order = ["1", "2", "3", "4", "5", "6"]
    print(classification_report(
        test_labels_tax, pred_tax, labels=labels_order,
        target_names=["Erinnern", "Verstehen", "Anwenden", "Analysieren", "Bewerten", "Erschaffen"],
        digits=3, zero_division=0
    ))

    tax_path = MODELS_DIR / "svm_taxonomy.pkl"
    joblib.dump(clf_tax, tax_path)
    print(f"  Gespeichert: {tax_path}")

    meta = {"model_name": MODEL_NAME, "embedding_dim": train_emb.shape[1]}
    joblib.dump(meta, MODELS_DIR / "meta.pkl")
    print(f"\nFertig. Modelle in {MODELS_DIR}/")


if __name__ == "__main__":
    main()
