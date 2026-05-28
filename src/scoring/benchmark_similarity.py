"""Benchmark: TF-IDF vs SentenceTransformer embeddings.

Compara calidad y performance de ambos backends sobre un sample de procesos.
Uso: uv run --python 3.11 python -m src.scoring.benchmark_similarity
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd

from src.scoring.semantic_similarity import (
    SentenceTransformerProvider,
    TfidfSimilarityProvider,
)


def load_sample_texts(n: int = 200) -> list[str]:
    marts_dir = Path(__file__).resolve().parents[2] / "data" / "marts"
    ranking_path = marts_dir / "ranking.parquet"
    if ranking_path.exists():
        df = pd.read_parquet(ranking_path)
        if "explanation" in df.columns:
            texts = df["explanation"].fillna("").astype(str).tolist()[:n]
            if len(texts) >= 10:
                return texts
    return [
        f"Proceso de contratacion numero {i} para adquisicion de bienes y servicios"
        for i in range(n)
    ]


def benchmark_backend(name: str, provider, texts: list[str]) -> dict:
    print(f"\n{'='*60}")
    print(f"Benchmark: {name}")
    print(f"{'='*60}")
    print(f"Textos: {len(texts)}")

    start = time.perf_counter()
    matrix = provider.matrix(texts)
    elapsed = time.perf_counter() - start

    print(f"Tiempo: {elapsed:.2f}s")
    print(f"Matriz: {matrix.shape}")

    upper_tri = matrix[np.triu_indices_from(matrix, k=1)]
    stats = {
        "name": name,
        "n_texts": len(texts),
        "time_seconds": round(elapsed, 3),
        "mean_similarity": round(float(upper_tri.mean()), 4),
        "median_similarity": round(float(np.median(upper_tri)), 4),
        "std_similarity": round(float(upper_tri.std()), 4),
        "min_similarity": round(float(upper_tri.min()), 4),
        "max_similarity": round(float(upper_tri.max()), 4),
        "p95_similarity": round(float(np.percentile(upper_tri, 95)), 4),
    }

    print("\nEstadísticas de similitud (triángulo superior):")
    print(f"  Media:   {stats['mean_similarity']:.4f}")
    print(f"  Mediana: {stats['median_similarity']:.4f}")
    print(f"  Std:     {stats['std_similarity']:.4f}")
    print(f"  Min:     {stats['min_similarity']:.4f}")
    print(f"  Max:     {stats['max_similarity']:.4f}")
    print(f"  P95:     {stats['p95_similarity']:.4f}")

    return stats


def main() -> None:
    print("Benchmark: TF-IDF vs SentenceTransformer (MiniLM multilingüe)")
    print("="*60)

    texts = load_sample_texts(200)
    print(f"\nSample: {len(texts)} textos")
    print(f"Ejemplo: {texts[0][:80]}...")

    results = []

    tfidf = TfidfSimilarityProvider()
    results.append(benchmark_backend("TF-IDF (baseline)", tfidf, texts))

    try:
        transformer = SentenceTransformerProvider()
        results.append(benchmark_backend(
            "SentenceTransformer (paraphrase-multilingual-MiniLM-L12-v2)",
            transformer,
            texts,
        ))
    except Exception as e:
        print(f"\n⚠️  No se pudo cargar SentenceTransformer: {e}")
        print("   Instala con: uv pip install sentence-transformers")

    if len(results) == 2:
        print(f"\n{'='*60}")
        print("COMPARACIÓN")
        print(f"{'='*60}")
        tfidf_r, trans_r = results
        speedup = tfidf_r["time_seconds"] / trans_r["time_seconds"]
        print(f"Speedup TF-IDF vs Transformer: {speedup:.2f}x")
        print("  (TF-IDF es más rápido, pero Transformer captura semántica)")

        delta_mean = trans_r["mean_similarity"] - tfidf_r["mean_similarity"]
        delta_std = trans_r["std_similarity"] - tfidf_r["std_similarity"]
        print(f"\nDiferencia en similitud media: {delta_mean:+.4f}")
        print(f"Diferencia en std: {delta_std:+.4f}")

        if trans_r["std_similarity"] > tfidf_r["std_similarity"]:
            print("\n✓ Transformer tiene mayor varianza → mejor discriminación")
        else:
            print("\n⚠️  TF-IDF tiene mayor varianza")

    output_path = Path(__file__).resolve().parents[2] / "validation" / "similarity_benchmark.json"
    output_path.parent.mkdir(exist_ok=True)
    import json
    output_path.write_text(json.dumps(results, indent=2))
    print(f"\nResultados guardados en: {output_path}")


if __name__ == "__main__":
    main()
