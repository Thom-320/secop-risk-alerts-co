from __future__ import annotations

import os
from dataclasses import dataclass
from logging import getLogger
from typing import Protocol

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_logger = getLogger(__name__)


class SimilarityProvider(Protocol):
    name: str

    def matrix(self, left_texts: list[str], right_texts: list[str] | None = None) -> np.ndarray:
        ...


@dataclass
class TfidfSimilarityProvider:
    name: str = "tfidf"
    ngram_range: tuple[int, int] = (1, 2)

    def matrix(self, left_texts: list[str], right_texts: list[str] | None = None) -> np.ndarray:
        right = right_texts if right_texts is not None else left_texts
        if not left_texts or not right:
            return np.zeros((len(left_texts), len(right)), dtype=float)
        vectorizer = TfidfVectorizer(stop_words=None, min_df=1, ngram_range=self.ngram_range)
        vectors = vectorizer.fit_transform(left_texts + right)
        left_matrix = vectors[: len(left_texts)]
        right_matrix = vectors[len(left_texts) :]
        return cosine_similarity(left_matrix, right_matrix)


@dataclass
class SentenceTransformerProvider:
    name: str = "sentence-transformer"
    model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"
    _model: object = None

    def _load_model(self) -> object:
        if self._model is not None:
            return self._model
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
            _logger.info(
                "Cargado modelo SentenceTransformer: %s",
                self.model_name,
            )
        except Exception as exc:
            _logger.warning(
                "No se pudo cargar SentenceTransformer %s: %s. "
                "Usa CONTRATIA_USE_TRANSFORMER_EMBEDDINGS=0 para forzar TF-IDF.",
                self.model_name,
                exc,
            )
            raise
        return self._model

    def matrix(self, left_texts: list[str], right_texts: list[str] | None = None) -> np.ndarray:
        right = right_texts if right_texts is not None else left_texts
        if not left_texts or not right:
            return np.zeros((len(left_texts), len(right)), dtype=float)
        model = self._load_model()
        left_embeddings = model.encode(left_texts, convert_to_numpy=True)
        right_embeddings = model.encode(right, convert_to_numpy=True)
        left_norm = left_embeddings / np.linalg.norm(left_embeddings, axis=1, keepdims=True)
        right_norm = right_embeddings / np.linalg.norm(right_embeddings, axis=1, keepdims=True)
        return np.dot(left_norm, right_norm.T)


def get_similarity_provider() -> SimilarityProvider:
    use_transformer = os.getenv("CONTRATIA_USE_TRANSFORMER_EMBEDDINGS", "0").strip() == "1"
    if use_transformer:
        try:
            provider = SentenceTransformerProvider()
            _ = provider._load_model()
            return provider
        except Exception:
            _logger.warning(
                "CONTRATIA_USE_TRANSFORMER_EMBEDDINGS=1 pero no se pudo cargar "
                "el modelo SentenceTransformer. Usando TF-IDF como fallback."
            )
    return TfidfSimilarityProvider()


def semantic_similarity_matrix(
    left_texts: list[str],
    right_texts: list[str] | None = None,
    provider: SimilarityProvider | None = None,
) -> np.ndarray:
    active_provider = provider or get_similarity_provider()
    return active_provider.matrix(left_texts, right_texts)
