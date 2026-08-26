from __future__ import annotations

import re
from dataclasses import asdict
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from .config import MIN_RETRIEVAL_SCORE, TOP_K
from .knowledge import load_chunks
from .models import DocumentChunk, RetrievalResult

class Retriever:
    """Small local RAG index.

    Uses TF-IDF word + character n-gram vectors so the project has no external
    vector database. Authority metadata is applied after semantic retrieval.
    """

    def __init__(self, knowledge_dir: Path):
        self.chunks: list[DocumentChunk] = load_chunks(knowledge_dir)
        corpus = [self._search_text(c) for c in self.chunks]
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=1,
        )
        self.matrix = normalize(self.vectorizer.fit_transform(corpus))

    @staticmethod
    def _search_text(chunk: DocumentChunk) -> str:
        meta = chunk.metadata
        return " ".join([
            chunk.filename,
            chunk.heading,
            str(meta.get("title", "")),
            str(meta.get("audience", "")),
            str(meta.get("policy_authority", "")),
            chunk.text,
        ])

    @staticmethod
    def _authority_bonus(chunk: DocumentChunk) -> float:
        m = chunk.metadata
        score = 0.0
        if str(m.get("status", "")).lower() == "active":
            score += 0.50
        if str(m.get("policy_authority", "")).lower() == "official":
            score += 0.25
        if str(m.get("audience", "")).lower() == "customer":
            score += 0.08
        if "legacy" in chunk.filename.lower() or str(m.get("status", "")).lower() in {"superseded", "draft"}:
            score -= 0.65
        if "internal" in chunk.filename.lower() or str(m.get("audience", "")).lower() == "internal":
            score -= 1.00
        return score

    def search(self, query: str, top_k: int = TOP_K) -> list[RetrievalResult]:
        q = normalize(self.vectorizer.transform([query]))
        scores = (self.matrix @ q.T).toarray().ravel()
        ranked = np.argsort(-scores)

        results: list[RetrievalResult] = []
        for idx in ranked[: max(top_k * 3, top_k)]:
            semantic = float(scores[idx])
            if semantic < MIN_RETRIEVAL_SCORE:
                continue
            chunk = self.chunks[idx]
            metadata = chunk.metadata
            if str(metadata.get("audience", "")).lower() == "internal":
                continue
            if str(metadata.get("customer_answering", "true")).lower() == "false":
                continue
            authority = self._authority_bonus(chunk)
            final = semantic + authority
            results.append(RetrievalResult(chunk, semantic, authority, final))

        results.sort(key=lambda x: x.final_score, reverse=True)
        return results[:top_k]

    def trace(self, results: list[RetrievalResult]) -> list[dict]:
        return [{
            "filename": r.chunk.filename,
            "heading": r.chunk.heading,
            "score": round(r.semantic_score, 4),
            "authority_bonus": round(r.authority_score, 4),
            "final_score": round(r.final_score, 4),
            "metadata": r.chunk.metadata,
            "lines": f"{r.chunk.start_line}-{r.chunk.end_line}",
        } for r in results]
