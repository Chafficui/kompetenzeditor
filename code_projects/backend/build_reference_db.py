#!/usr/bin/env python3
"""
Berechnet Embeddings für den Gold-Standard und speichert sie als Referenz-Datenbank.

Filtert "schlecht"-Sätze heraus, damit das Empfehlungssystem nur
qualitativ hochwertige Formulierungen vorschlägt.

Nutzung:
    python build_reference_db.py
"""

import csv
import json
import time
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "T-Systems-onsite/cross-en-de-roberta-sentence-transformer"
BASE_DIR = Path(__file__).parent
DATA_CSV = BASE_DIR.parent.parent / "data" / "goldstandard.csv"
MODELS_DIR = BASE_DIR / "models"


def main():
    MODELS_DIR.mkdir(exist_ok=True)

    print("Lade Daten...")
    with open(DATA_CSV, encoding="utf-8") as f:
        all_rows = list(csv.DictReader(f))
    print(f"  {len(all_rows)} Sätze insgesamt")

    rows = [r for r in all_rows if r.get("qualitaet", "").strip().lower() != "schlecht"]
    excluded = len(all_rows) - len(rows)
    print(f"  {excluded} 'schlecht'-Sätze gefiltert → {len(rows)} in Referenz-DB")

    print(f"\nLade SBERT-Modell: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    sentences = [r["satz"] for r in rows]

    print("\nBerechne Embeddings...")
    t0 = time.time()
    embeddings = model.encode(sentences, show_progress_bar=True, batch_size=64)
    elapsed = time.time() - t0
    print(f"  {len(sentences)} Sätze in {elapsed:.1f}s ({len(sentences)/elapsed:.0f} Sätze/s)")

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings_normed = embeddings / (norms + 1e-10)

    emb_path = MODELS_DIR / "reference_embeddings.npy"
    np.save(emb_path, embeddings_normed.astype(np.float32))
    print(f"  Embeddings: {emb_path} ({embeddings_normed.shape})")

    metadata = []
    for r in rows:
        metadata.append({
            "satz": r["satz"],
            "typ": r["typ"],
            "taxonomie": r.get("taxonomie", ""),
            "qualitaet": r.get("qualitaet", ""),
            "modulname": r.get("modulname", ""),
            "studiengang": r.get("studiengang", ""),
            "hochschule": r.get("hochschule", ""),
        })

    meta_path = MODELS_DIR / "reference_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=None)
    print(f"  Metadaten: {meta_path}")

    print(f"\nFertig. Referenz-DB mit {len(metadata)} Einträgen ({excluded} 'schlecht' ausgeschlossen).")


if __name__ == "__main__":
    main()
