import time
import hashlib
import re
import threading
from typing import Optional, Dict, Any, List
import numpy as np

try:
    from backend.src.config import (
        CACHE_ENABLED,
        CACHE_SIMILARITY_THRESHOLD,
        CACHE_TTL_SECONDS,
    )
except ImportError:
    from src.config import (
        CACHE_ENABLED,
        CACHE_SIMILARITY_THRESHOLD,
        CACHE_TTL_SECONDS,
    )



def _normalize_text(text: str) -> str:
    """Normalize text by lowercasing, removing extra whitespace and punctuation."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text)


def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculate cosine similarity between two float vectors."""
    a = np.array(vec_a, dtype=float)
    b = np.array(vec_b, dtype=float)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


class ResponseCache:
    """Dual-tier response cache: Exact normalized hash match and semantic similarity match."""

    def __init__(self):
        self._lock = threading.Lock()
        self._exact_cache: Dict[str, Dict[str, Any]] = {}
        self._semantic_entries: List[Dict[str, Any]] = []
        self._hits = 0
        self._misses = 0

    def _generate_hash(self, text: str) -> str:
        norm = _normalize_text(text)
        return hashlib.sha256(norm.encode("utf-8")).hexdigest()

    def get(
        self, query: str, query_embedding: Optional[List[float]] = None
    ) -> Optional[Dict[str, Any]]:
        """Retrieve cached response if available and not expired."""
        if not CACHE_ENABLED:
            return None

        current_time = time.time()
        query_hash = self._generate_hash(query)

        with self._lock:
            # 1. Check exact normalized hash match
            if query_hash in self._exact_cache:
                entry = self._exact_cache[query_hash]
                if current_time - entry["timestamp"] <= CACHE_TTL_SECONDS:
                    self._hits += 1
                    return {
                        "answer": entry["answer"],
                        "sources": entry["sources"],
                        "escalated": entry["escalated"],
                        "cache_type": "exact",
                    }
                else:
                    del self._exact_cache[query_hash]

            # 2. Check semantic similarity match if query embedding is provided
            if query_embedding and self._semantic_entries:
                best_similarity = 0.0
                best_entry = None

                for item in self._semantic_entries:
                    if current_time - item["timestamp"] > CACHE_TTL_SECONDS:
                        continue
                    sim = _cosine_similarity(query_embedding, item["embedding"])
                    if sim > best_similarity:
                        best_similarity = sim
                        best_entry = item

                if best_similarity >= CACHE_SIMILARITY_THRESHOLD and best_entry:
                    self._hits += 1
                    return {
                        "answer": best_entry["answer"],
                        "sources": best_entry["sources"],
                        "escalated": best_entry["escalated"],
                        "cache_type": f"semantic (similarity: {best_similarity:.2f})",
                    }

            self._misses += 1
            return None

    def set(
        self,
        query: str,
        answer: str,
        sources: List[str],
        escalated: bool,
        query_embedding: Optional[List[float]] = None,
    ):
        """Store query result in exact and semantic cache layers."""
        if not CACHE_ENABLED or escalated:
            # Do not cache out-of-scope escalations as permanent answers
            return

        current_time = time.time()
        query_hash = self._generate_hash(query)

        cache_record = {
            "query": query,
            "answer": answer,
            "sources": sources,
            "escalated": escalated,
            "timestamp": current_time,
        }

        with self._lock:
            self._exact_cache[query_hash] = cache_record

            if query_embedding:
                self._semantic_entries.append({
                    **cache_record,
                    "embedding": query_embedding,
                })
                # Limit memory growth to last 500 semantic entries
                if len(self._semantic_entries) > 500:
                    self._semantic_entries.pop(0)

    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._exact_cache.clear()
            self._semantic_entries.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Return cache performance statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0.0
            return {
                "enabled": CACHE_ENABLED,
                "exact_entries": len(self._exact_cache),
                "semantic_entries": len(self._semantic_entries),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate_pct": round(hit_rate, 2),
            }


# Singleton cache instance
response_cache = ResponseCache()
