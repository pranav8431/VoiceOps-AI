"""Benchmark: token generation endpoint latency."""

import statistics
import time

from fastapi.testclient import TestClient

from app.main import app


def test_token_latency(bench_rounds):
    client = TestClient(app)
    latencies = []

    for _ in range(bench_rounds):
        start = time.perf_counter()
        res = client.post("/api/token", json={"room": "bench-room"})
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert res.status_code == 200
        latencies.append(elapsed_ms)

    latencies.sort()
    p50 = statistics.median(latencies)
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    mean = statistics.mean(latencies)

    print(f"\n{'='*50}")
    print(f"Token Generation Latency ({bench_rounds} rounds)")
    print(f"{'='*50}")
    print(f"  Mean:  {mean:.2f} ms")
    print(f"  p50:   {p50:.2f} ms")
    print(f"  p95:   {p95:.2f} ms")
    print(f"  p99:   {p99:.2f} ms")
    print(f"  Min:   {min(latencies):.2f} ms")
    print(f"  Max:   {max(latencies):.2f} ms")
    print(f"{'='*50}")

    assert p50 < 100, f"p50 latency {p50:.2f}ms exceeds 100ms threshold"
    assert p95 < 200, f"p95 latency {p95:.2f}ms exceeds 200ms threshold"
