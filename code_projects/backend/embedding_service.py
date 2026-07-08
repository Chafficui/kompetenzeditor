"""
Embedding-Service: SBERT-Encoding und SVM-Klassifikation.
"""

from pathlib import Path

import joblib
import numpy as np
from sentence_transformers import SentenceTransformer

MODELS_DIR = Path(__file__).parent / "models"
MODEL_NAME = "T-Systems-onsite/cross-en-de-roberta-sentence-transformer"


class EmbeddingService:
    def __init__(self):
        self.model: SentenceTransformer | None = None
        self.clf_type = None
        self.clf_taxonomy = None

    def load(self):
        """Lädt SBERT-Modell und SVM-Klassifikatoren."""
        print(f"  Lade SBERT: {MODEL_NAME}")
        self.model = SentenceTransformer(MODEL_NAME)

        type_path = MODELS_DIR / "svm_type.pkl"
        tax_path = MODELS_DIR / "svm_taxonomy.pkl"

        if type_path.exists():
            self.clf_type = joblib.load(type_path)
            print(f"  SVM-Type geladen: {type_path}")
        else:
            print(f"  WARNUNG: {type_path} nicht gefunden. Bitte train_classifiers.py ausführen.")

        if tax_path.exists():
            self.clf_taxonomy = joblib.load(tax_path)
            print(f"  SVM-Taxonomy geladen: {tax_path}")
        else:
            print(f"  WARNUNG: {tax_path} nicht gefunden. Bitte train_classifiers.py ausführen.")

    def encode(self, sentences: list[str]) -> np.ndarray:
        """Berechnet Embeddings für eine Liste von Sätzen."""
        embeddings = self.model.encode(sentences, batch_size=64, show_progress_bar=False)
        return np.array(embeddings)

    def encode_normalized(self, sentences: list[str]) -> np.ndarray:
        """Berechnet normalisierte Embeddings (für Cosine-Similarity via dot product)."""
        emb = self.encode(sentences)
        norms = np.linalg.norm(emb, axis=1, keepdims=True)
        return emb / (norms + 1e-10)

    def classify_type(self, embedding: np.ndarray) -> tuple[str, float]:
        """Klassifiziert Satztyp (K/I/S) mit Konfidenz."""
        if self.clf_type is None:
            return "K", 0.5  # Fallback

        emb_2d = embedding.reshape(1, -1)
        pred = self.clf_type.predict(emb_2d)[0]
        proba = self.clf_type.predict_proba(emb_2d)[0]
        confidence = float(proba.max())
        return pred, confidence

    def classify_taxonomy(self, embedding: np.ndarray) -> tuple[int, float]:
        """Klassifiziert Taxonomiestufe (1-6) mit Konfidenz."""
        if self.clf_taxonomy is None:
            return 3, 0.5  # Fallback

        emb_2d = embedding.reshape(1, -1)
        pred = self.clf_taxonomy.predict(emb_2d)[0]
        proba = self.clf_taxonomy.predict_proba(emb_2d)[0]
        confidence = float(proba.max())
        return int(pred), confidence
