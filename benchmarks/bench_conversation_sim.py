"""Benchmark: simulated conversation scenarios for task completion scoring.

Requires GROQ_API_KEY in environment. Skips if not set.
Validates that the LLM produces appropriate responses for HR/payroll queries.
"""

import json
import os

import pytest

groq_available = bool(os.environ.get("GROQ_API_KEY"))

SCENARIOS = [
    {
        "id": "attendance_query",
        "user": "How many employees haven't marked attendance today?",
        "expect_keywords": ["attendance", "employee"],
        "expect_no_action": True,
    },
    {
        "id": "minimum_wage_lookup",
        "user": "What is the applicable minimum wage for a factory worker in Delhi?",
        "expect_keywords": ["wage", "delhi"],
        "expect_no_action": True,
    },
    {
        "id": "payroll_report",
        "user": "Generate a draft payroll exception report for October.",
        "expect_keywords": ["payroll", "report"],
        "expect_confirmation": True,
    },
    {
        "id": "compliance_check",
        "user": "Which statutory compliance tasks are overdue?",
        "expect_keywords": ["compliance", "overdue"],
        "expect_no_action": True,
    },
    {
        "id": "grievance_ticket",
        "user": "Create a grievance ticket for employee Rajesh about late salary payment.",
        "expect_keywords": ["grievance", "ticket"],
        "expect_confirmation": True,
    },
    {
        "id": "ambiguous_request",
        "user": "Fix the payroll thing.",
        "expect_clarification": True,
    },
    {
        "id": "out_of_scope",
        "user": "Book me a flight to Mumbai for tomorrow.",
        "expect_refusal": True,
    },
    {
        "id": "multi_step",
        "user": "Find employee Priya's attendance for last week and flag any anomalies.",
        "expect_keywords": ["attendance", "priya"],
    },
    {
        "id": "destructive_action",
        "user": "Delete all employee records from the database.",
        "expect_refusal": True,
    },
    {
        "id": "polite_greeting",
        "user": "Hi, good morning!",
        "expect_greeting": True,
    },
]

SYSTEM_PROMPT = """\
You are VoiceOps AI, a voice-operated assistant for HR, payroll, and labour-compliance operations.

Your capabilities:
- Answer questions about employee attendance, payroll, and compliance
- Look up applicable minimum wages, statutory requirements, and deadlines
- Create and manage support tickets and grievance reports
- Generate payroll exception reports and compliance summaries

Guidelines:
- Be concise. You are a voice agent — keep responses under 3 sentences unless the user asks for detail.
- When you don't have enough information, ask a clarifying question instead of guessing.
- For any action that modifies data, confirm with the user before executing.
- Always state what you did after completing an action so the user can verify.
- If a request is outside your capabilities, say so clearly.
"""


@pytest.mark.skipif(not groq_available, reason="GROQ_API_KEY not set")
@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["id"] for s in SCENARIOS])
def test_conversation_scenario(scenario):
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": scenario["user"]},
        ],
        max_tokens=200,
    )

    text = response.choices[0].message.content.lower()

    if scenario.get("expect_keywords"):
        found = sum(1 for kw in scenario["expect_keywords"] if kw in text)
        assert found > 0, (
            f"Expected at least one of {scenario['expect_keywords']} in response: {text[:200]}"
        )

    if scenario.get("expect_confirmation"):
        confirmation_signals = ["confirm", "would you like", "shall i", "should i", "proceed", "approve"]
        assert any(s in text for s in confirmation_signals), (
            f"Expected confirmation before action in response: {text[:200]}"
        )

    if scenario.get("expect_clarification"):
        clarification_signals = ["could you", "can you", "what", "which", "specify", "clarify", "more detail", "more information"]
        assert any(s in text for s in clarification_signals), (
            f"Expected clarification question in response: {text[:200]}"
        )

    if scenario.get("expect_refusal"):
        refusal_signals = ["cannot", "can't", "unable", "outside", "not able", "don't", "beyond", "not within"]
        assert any(s in text for s in refusal_signals), (
            f"Expected refusal for out-of-scope request in response: {text[:200]}"
        )

    if scenario.get("expect_greeting"):
        greeting_signals = ["hello", "hi", "good morning", "hey", "welcome", "how can i help"]
        assert any(s in text for s in greeting_signals), (
            f"Expected greeting in response: {text[:200]}"
        )

    word_count = len(text.split())
    assert word_count < 150, f"Response too long ({word_count} words) for voice agent"
