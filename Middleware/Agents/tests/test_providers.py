"""Offline tests for the pluggable LLM provider resolution."""
from __future__ import annotations

import pytest

from epaa.providers import llm


def _settings(**kw):
    return type("S", (), kw)()


def test_heuristic_provider_raises_unavailable(monkeypatch):
    monkeypatch.setattr(llm, "get_settings", lambda: _settings(llm_provider="heuristic"))
    with pytest.raises(llm.LLMUnavailable):
        llm.complete("sys", "hi")


def test_unreachable_ollama_falls_through_to_unavailable(monkeypatch):
    monkeypatch.setattr(
        llm,
        "get_settings",
        lambda: _settings(llm_provider="ollama", ollama_base_url="http://127.0.0.1:1", ollama_model="x"),
    )
    with pytest.raises(llm.LLMUnavailable):
        llm.complete("sys", "hi")


def test_all_backends_registered():
    assert set(llm._BACKENDS) == {"strands", "bedrock", "langchain", "openai", "ollama"}
