"""
Ähnlichkeitssuche: Cosine-Top-k gegen vorberechnete Referenz-Embeddings.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

MODELS_DIR = Path(__file__).parent / "models"


@dataclass
class SimilarSentence:
    satz: str
    similarity: float
    typ: str
    taxonomie: str
    modulname: str
    studiengang: str


class SimilaritySearch:
    def __init__(self):
        self.embeddings: np.ndarray | None = None
        self.metadata: list[dict] | None = None

    def load(self):
        """Lädt vorberechnete Referenz-Embeddings und Metadaten."""
        emb_path = MODELS_DIR / "reference_embeddings.npy"
        meta_path = MODELS_DIR / "reference_metadata.json"

        if not emb_path.exists() or not meta_path.exists():
            print("  WARNUNG: Referenz-DB nicht gefunden. Bitte build_reference_db.py ausführen.")
            return

        self.embeddings = np.load(emb_path)
        with open(meta_path, encoding="utf-8") as f:
            self.metadata = json.load(f)

        print(f"  Referenz-DB geladen: {self.embeddings.shape[0]} Sätze, {self.embeddings.shape[1]}d")

    def find_similar(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        filter_typ: str | None = None,
        filter_taxonomie: str | None = None,
        exclude_text: str | None = None,
    ) -> list[SimilarSentence]:
        """Findet die top_k ähnlichsten Sätze aus der Referenz-DB."""
        if self.embeddings is None or self.metadata is None:
            return []

        # Normalisiere Query-Embedding
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)

        # Cosine-Similarity via dot product (Referenz ist bereits normalisiert)
        similarities = self.embeddings @ query_norm

        # Filter anwenden
        mask = np.ones(len(self.metadata), dtype=bool)
        if filter_typ:
            mask &= np.array([m["typ"] == filter_typ for m in self.metadata])
        if filter_taxonomie:
            mask &= np.array([m["taxonomie"] == filter_taxonomie for m in self.metadata])
        if exclude_text:
            mask &= np.array([m["satz"] != exclude_text for m in self.metadata])

        # Maskierte Similarities
        masked_sim = np.where(mask, similarities, -1.0)

        # Top-k Indizes
        top_indices = np.argsort(masked_sim)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if masked_sim[idx] <= 0:
                continue
            meta = self.metadata[idx]
            results.append(SimilarSentence(
                satz=meta["satz"],
                similarity=float(masked_sim[idx]),
                typ=meta["typ"],
                taxonomie=meta["taxonomie"],
                modulname=meta["modulname"],
                studiengang=meta["studiengang"],
            ))

        return results
