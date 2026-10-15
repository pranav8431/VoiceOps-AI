"""Benchmark: Groq LLM inference latency (time to first token, total response).

Requires GROQ_API_KEY in environment. Skips if not set.
"""

import os
import statistics
import time

import pytest

groq_available = bool(os.environ.get("GROQ_API_KEY"))


@pytest.mark.skipif(not groq_available, reason="GROQ_API_KEY not set")
def test_groq_first_token_latency(bench_rounds):
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )

    ttft_list = []
    total_list = []

    prompts = [
        "How many employees haven't marked attendance today?",
        "What is the minimum wage for category A workers in Maharashtra?",
        "Generate a payroll exception summary.",
        "Which compliance tasks are overdue this month?",
        "Create a grievance ticket for employee ID 1042.",
    ]

    for i in range(bench_rounds):
        prompt = prompts[i % len(prompts)]
        start = time.perf_counter()
        first_token_time = None

        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a concise HR assistant. Reply in under 2 sentences.",
                },
                {"role": "user", "content": prompt},
            ],
            stream=True,
            max_tokens=150,
        )

        for chunk in stream:
            if first_token_time is None and chunk.choices[0].delta.content:
                first_token_time = time.perf_counter()

        total_time = time.perf_counter() - start

        if first_token_time:
            ttft_list.append((first_token_time - start) * 1000)
        total_list.append(total_time * 1000)

    print(f"\n{'='*50}")
    print(f"Groq LLM Latency ({bench_rounds} rounds)")
    print(f"{'='*50}")

    if ttft_list:
        ttft_list.sort()
        print(f"  Time to First Token (TTFT):")
        print(f"    Mean:  {statistics.mean(ttft_list):.0f} ms")
        print(f"    p50:   {statistics.median(ttft_list):.0f} ms")
        print(f"    p95:   {ttft_list[int(len(ttft_list)*0.95)]:.0f} ms")

    total_list.sort()
    print(f"  Total Response Time:")
    print(f"    Mean:  {statistics.mean(total_list):.0f} ms")
    print(f"    p50:   {statistics.median(total_list):.0f} ms")
    print(f"    p95:   {total_list[int(len(total_list)*0.95)]:.0f} ms")
    print(f"{'='*50}")

    if ttft_list:
        assert statistics.median(ttft_list) < 500, "TTFT p50 exceeds 500ms"
