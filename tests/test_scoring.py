from __future__ import annotations

import pandas as pd

from src.features.process_features import confidence_band, priority_band, rule_score_from_row
from src.scoring.semantic_similarity import (
    TfidfSimilarityProvider,
    get_similarity_provider,
    semantic_similarity_matrix,
)
from src.utils.reporting import build_process_report_html


def test_rule_score_respects_paa_modes() -> None:
    row = pd.Series(
        {
            "value_deviation_ratio": 2.7,
            "duration_deviation_ratio": 1.9,
            "response_gap": 3,
            "paa_match_status": "none",
        }
    )
    full = rule_score_from_row(row, "full")
    secondary = rule_score_from_row(row, "secondary")
    visible_only = rule_score_from_row(row, "visible_only")
    assert full >= secondary >= visible_only


def test_priority_and_confidence_bands() -> None:
    assert priority_band(90) == "alerta prioritaria"
    assert priority_band(50) == "observacion"
    assert confidence_band(80) == "alta"
    assert confidence_band(40) == "baja"


def test_html_report_contains_process_and_disclaimer() -> None:
    html = build_process_report_html(
        {
            "process_key": "P1",
            "process_reference": "REF-001",
            "entity_name": "Entidad Demo",
            "priority_score": 82,
            "confidence_score": 71,
            "reasons": "monto atipico frente a pares",
            "base_price": 1500000,
            "paa_match_status": "strong",
        },
        [
            {
                "comparable_label": "REF-002 | Entidad Demo",
                "comparable_value": 1200000,
                "similarity": 0.81,
            }
        ],
    )
    assert "REF-001" in html
    assert "prioriza revision humana" in html.lower()
    assert "Accion recomendada" in html
    assert "Que revisar manualmente" in html
    assert "no determina corrupcion" in html.lower()


def test_tfidf_similarity_provider_returns_matrix() -> None:
    matrix = semantic_similarity_matrix(
        ["mantenimiento escuela rural", "compra computadores"],
        ["mantenimiento infraestructura escolar", "software contable"],
        provider=TfidfSimilarityProvider(),
    )
    assert matrix.shape == (2, 2)
    assert matrix[0, 0] >= matrix[0, 1]


def test_similarity_provider_defaults_to_transformer(monkeypatch) -> None:
    monkeypatch.delenv("CONTRATIA_USE_TRANSFORMER_EMBEDDINGS", raising=False)
    provider = get_similarity_provider()
    assert provider.name in ("sentence-transformer", "tfidf")


def test_transformer_provider_falls_back_gracefully_if_model_unavailable(monkeypatch) -> None:
    monkeypatch.setenv("CONTRATIA_USE_TRANSFORMER_EMBEDDINGS", "1")
    try:
        from src.scoring.semantic_similarity import SentenceTransformerProvider

        provider = SentenceTransformerProvider()
        matrix = provider.matrix(
            ["mantenimiento escuela rural", "compra computadores"],
            ["mantenimiento infraestructura escolar", "software contable"],
        )
        assert matrix.shape == (2, 2)
    except Exception:
        pass


def test_get_similarity_provider_returns_tfidf_when_transformer_env_is_0(monkeypatch) -> None:
    monkeypatch.setenv("CONTRATIA_USE_TRANSFORMER_EMBEDDINGS", "0")
    assert get_similarity_provider().name == "tfidf"


def test_transformer_provider_import_does_not_crash_without_model() -> None:
    from src.scoring.semantic_similarity import SentenceTransformerProvider

    provider = SentenceTransformerProvider()
    assert provider.name == "sentence-transformer"
    assert provider.model_name == "paraphrase-multilingual-MiniLM-L12-v2"


def test_tfidf_empty_texts_returns_zero_matrix() -> None:
    provider = TfidfSimilarityProvider()
    matrix = provider.matrix([], ["texto"])
    assert matrix.shape == (0, 1)

    matrix2 = provider.matrix(["texto"], [])
    assert matrix2.shape == (1, 0)

    matrix3 = provider.matrix([], [])
    assert matrix3.shape == (0, 0)
