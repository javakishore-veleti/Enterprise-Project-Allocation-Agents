"""LLM access for the reasoning agents.

Resolution order (LLM_PROVIDER=auto): Strands Agents → Bedrock (boto3) → unavailable.
Callers treat ``LLMUnavailable`` as "use the deterministic heuristic instead", so
the whole pipeline runs offline with no AWS and no Strands installed.
"""
from __future__ import annotations

import json
import logging

from ..config import get_settings

log = logging.getLogger(__name__)


class LLMUnavailable(RuntimeError):
    """Raised when no LLM backend is usable; callers fall back to heuristics."""


def _complete_strands(system: str, prompt: str) -> str:
    from strands import Agent
    from strands.models import BedrockModel

    s = get_settings()
    model = BedrockModel(model_id=s.bedrock_model_id, region_name=s.aws_region)
    agent = Agent(model=model, system_prompt=system)
    return str(agent(prompt)).strip()


def _complete_bedrock(system: str, prompt: str) -> str:
    import boto3

    s = get_settings()
    client = boto3.client("bedrock-runtime", region_name=s.aws_region)
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = client.invoke_model(modelId=s.bedrock_model_id, body=json.dumps(body))
    return json.loads(resp["body"].read())["content"][0]["text"].strip()


def complete(system: str, prompt: str) -> str:
    """Return an LLM completion or raise LLMUnavailable."""
    provider = get_settings().llm_provider.lower()
    order = {
        "auto": ("strands", "bedrock"),
        "strands": ("strands",),
        "bedrock": ("bedrock",),
        "heuristic": (),
    }.get(provider, ("strands", "bedrock"))

    for backend in order:
        try:
            return _complete_strands(system, prompt) if backend == "strands" else _complete_bedrock(system, prompt)
        except Exception as exc:  # noqa: BLE001 — try next backend / fall back
            log.warning("LLM backend '%s' unavailable: %s", backend, exc)
    raise LLMUnavailable(f"no LLM backend available for provider='{provider}'")


def complete_json(system: str, prompt: str) -> dict:
    """Complete and parse a JSON object from the response (tolerant of code fences)."""
    text = complete(system, prompt)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise LLMUnavailable("LLM did not return JSON")
    return json.loads(text[start : end + 1])
