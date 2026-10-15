"""Metrics collection and reporting utilities for benchmarks."""

import json
import statistics
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class BenchmarkResult:
    name: str
    rounds: int
    latencies_ms: list[float] = field(default_factory=list)
    successes: int = 0
    failures: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        total = self.successes + self.failures
        return (self.successes / total * 100) if total > 0 else 0.0

    @property
    def p50(self) -> float:
        return statistics.median(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def p95(self) -> float:
        if not self.latencies_ms:
            return 0.0
        s = sorted(self.latencies_ms)
        return s[int(len(s) * 0.95)]

    @property
    def mean(self) -> float:
        return statistics.mean(self.latencies_ms) if self.latencies_ms else 0.0

    def summary(self) -> dict:
        return {
            "name": self.name,
            "rounds": self.rounds,
            "success_rate_pct": round(self.success_rate, 2),
            "latency_ms": {
                "mean": round(self.mean, 2),
                "p50": round(self.p50, 2),
                "p95": round(self.p95, 2),
            }
            if self.latencies_ms
            else None,
            "errors": self.errors[:5],
        }

    def print_report(self):
        s = self.summary()
        print(f"\n{'='*50}")
        print(f"  {s['name']} ({s['rounds']} rounds)")
        print(f"{'='*50}")
        print(f"  Success rate: {s['success_rate_pct']}%")
        if s["latency_ms"]:
            lat = s["latency_ms"]
            print(f"  Latency — mean: {lat['mean']}ms  p50: {lat['p50']}ms  p95: {lat['p95']}ms")
        if s["errors"]:
            print(f"  Errors: {s['errors']}")
        print(f"{'='*50}")


def save_results(results: list[BenchmarkResult], path: str = "benchmark_results.json"):
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "benchmarks": [r.summary() for r in results],
    }
    Path(path).write_text(json.dumps(output, indent=2))
    print(f"\nResults saved to {path}")
