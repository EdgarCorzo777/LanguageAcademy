import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from backend.src.config import METRICS_FILE, LLM_PROVIDER
except ImportError:
    from src.config import METRICS_FILE, LLM_PROVIDER


# Pricing per million tokens (USD)
COST_RATES = {
    "gemini": {
        "input_per_million": 0.075,
        "output_per_million": 0.30,
    },
    "openai": {
        "input_per_million": 0.50,
        "output_per_million": 1.50,
    },
}


class MetricsCollector:
    """Thread-safe collector for query usage, financial costs, escalations, and cache efficiency."""

    def __init__(self, storage_path: Path = METRICS_FILE):
        self.storage_path = storage_path
        self._lock = threading.Lock()
        self._total_queries = 0
        self._cache_hits = 0
        self._escalated_queries = 0
        self._prompt_tokens = 0
        self._completion_tokens = 0
        self._total_latency_ms = 0.0
        self._recent_events: List[Dict[str, Any]] = []
        self._load_from_disk()

    def _load_from_disk(self):
        """Load persisted metrics from JSON file if present."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._total_queries = data.get("total_queries", 0)
                    self._cache_hits = data.get("cache_hits", 0)
                    self._escalated_queries = data.get("escalated_queries", 0)
                    self._prompt_tokens = data.get("prompt_tokens", 0)
                    self._completion_tokens = data.get("completion_tokens", 0)
                    self._total_latency_ms = data.get("total_latency_ms", 0.0)
                    self._recent_events = data.get("recent_events", [])
            except Exception:
                pass

    def _persist_to_disk(self):
        """Save current metrics state to disk."""
        try:
            data = {
                "total_queries": self._total_queries,
                "cache_hits": self._cache_hits,
                "escalated_queries": self._escalated_queries,
                "prompt_tokens": self._prompt_tokens,
                "completion_tokens": self._completion_tokens,
                "total_latency_ms": self._total_latency_ms,
                "recent_events": self._recent_events[-50:],
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def record_query(
        self,
        query: str,
        latency_ms: float,
        escalated: bool,
        cached: bool = False,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        channel: str = "api",
    ):
        """Record query telemetry, token consumption, and escalation status."""
        with self._lock:
            self._total_queries += 1
            if cached:
                self._cache_hits += 1
            if escalated:
                self._escalated_queries += 1

            self._prompt_tokens += prompt_tokens
            self._completion_tokens += completion_tokens
            self._total_latency_ms += latency_ms

            # Estimate cost based on provider
            provider_rates = COST_RATES.get(LLM_PROVIDER, COST_RATES["gemini"])
            query_cost = (
                (prompt_tokens / 1_000_000.0) * provider_rates["input_per_million"]
                + (completion_tokens / 1_000_000.0) * provider_rates["output_per_million"]
            )

            event = {
                "timestamp": datetime.now().isoformat(),
                "query": query[:60] + "..." if len(query) > 60 else query,
                "latency_ms": round(latency_ms, 1),
                "cached": cached,
                "escalated": escalated,
                "tokens": prompt_tokens + completion_tokens,
                "cost_usd": round(query_cost, 6),
                "channel": channel,
            }
            self._recent_events.append(event)
            if len(self._recent_events) > 50:
                self._recent_events.pop(0)

            self._persist_to_disk()

    def get_metrics(self) -> Dict[str, Any]:
        """Compute aggregated KPIs, escalation rates, token usage, and cost estimates."""
        with self._lock:
            provider_rates = COST_RATES.get(LLM_PROVIDER, COST_RATES["gemini"])
            total_cost = (
                (self._prompt_tokens / 1_000_000.0) * provider_rates["input_per_million"]
                + (self._completion_tokens / 1_000_000.0) * provider_rates["output_per_million"]
            )

            avg_latency = (
                (self._total_latency_ms / self._total_queries)
                if self._total_queries > 0
                else 0.0
            )
            escalation_rate = (
                (self._escalated_queries / self._total_queries * 100.0)
                if self._total_queries > 0
                else 0.0
            )
            cache_hit_rate = (
                (self._cache_hits / self._total_queries * 100.0)
                if self._total_queries > 0
                else 0.0
            )

            return {
                "total_queries": self._total_queries,
                "cache_hits": self._cache_hits,
                "cache_hit_rate_pct": round(cache_hit_rate, 2),
                "escalated_queries": self._escalated_queries,
                "escalation_rate_pct": round(escalation_rate, 2),
                "total_tokens": self._prompt_tokens + self._completion_tokens,
                "prompt_tokens": self._prompt_tokens,
                "completion_tokens": self._completion_tokens,
                "estimated_cost_usd": round(total_cost, 6),
                "active_llm_provider": LLM_PROVIDER,
                "avg_latency_ms": round(avg_latency, 1),
                "recent_events": self._recent_events[-10:],
            }

    def reset(self):
        """Reset all metrics."""
        with self._lock:
            self._total_queries = 0
            self._cache_hits = 0
            self._escalated_queries = 0
            self._prompt_tokens = 0
            self._completion_tokens = 0
            self._total_latency_ms = 0.0
            self._recent_events.clear()
            self._persist_to_disk()


# Singleton metrics collector instance
metrics_collector = MetricsCollector()
