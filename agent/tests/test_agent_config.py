import os
import sys
from unittest.mock import patch, MagicMock

sys.modules["livekit"] = MagicMock()
sys.modules["livekit.rtc"] = MagicMock()
sys.modules["livekit.agents"] = MagicMock()
sys.modules["livekit.agents.pipeline"] = MagicMock()
sys.modules["livekit.plugins"] = MagicMock()
sys.modules["livekit.plugins.deepgram"] = MagicMock()
sys.modules["livekit.plugins.elevenlabs"] = MagicMock()
sys.modules["livekit.plugins.silero"] = MagicMock()
sys.modules["livekit.plugins.openai"] = MagicMock()


def _load_main():
    import importlib

    spec = importlib.util.spec_from_file_location(
        "agent_main",
        os.path.join(os.path.dirname(__file__), "..", "main.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_system_prompt_exists():
    mod = _load_main()
    assert hasattr(mod, "SYSTEM_PROMPT")
    assert len(mod.SYSTEM_PROMPT) > 100


def test_system_prompt_includes_core_capabilities():
    mod = _load_main()
    prompt = mod.SYSTEM_PROMPT.lower()
    assert "hr" in prompt or "payroll" in prompt
    assert "compliance" in prompt
    assert "voice" in prompt


def test_system_prompt_enforces_confirmation():
    mod = _load_main()
    prompt = mod.SYSTEM_PROMPT.lower()
    assert "confirm" in prompt


def test_system_prompt_enforces_brevity():
    mod = _load_main()
    prompt = mod.SYSTEM_PROMPT.lower()
    assert "concise" in prompt or "3 sentences" in prompt or "brief" in prompt


def test_entrypoint_is_callable():
    mod = _load_main()
    assert callable(mod.entrypoint)


def test_prewarm_is_callable():
    mod = _load_main()
    assert callable(mod.prewarm)
