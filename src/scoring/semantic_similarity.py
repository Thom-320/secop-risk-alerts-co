from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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


def get_similarity_provider() -> SimilarityProvider:
    return TfidfSimilarityProvider()


def semantic_similarity_matrix(
    left_texts: list[str],
    right_texts: list[str] | None = None,
    provider: SimilarityProvider | None = None,
) -> np.ndarray:
    active_provider = provider or get_similarity_provider()
    return active_provider.matrix(left_texts, right_texts)
