"""LLM access for the reasoning agents — pluggable across frameworks.

One interface (`complete`) over multiple backends so the same agents can run on
different stacks (the user's "exposure across frameworks" goal):

    LLM_PROVIDER = auto      # try strands → bedrock, else unavailable
                 | strands   # Strands Agents + Bedrock
                 | bedrock   # Bedrock via boto3
                 | langchain # LangChain (langchain-aws ChatBedrockConverse)
                 | openai    # OpenAI SDK (or OpenAI-compatible endpoint)
                 | ollama    # local HuggingFace/GGUF models via Ollama
                 | heuristic # no LLM — callers use their deterministic fallback

Every backend import is guarded; any failure raises ``LLMUnavailable`` and the
caller falls back to heuristics, so the pipeline always runs offline.
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


def _complete_langchain(system: str, prompt: str) -> str:
    from langchain_aws import ChatBedrockConverse
    from langchain_core.messages import HumanMessage, SystemMessage

    s = get_settings()
    chat = ChatBedrockConverse(model=s.bedrock_model_id, region_name=s.aws_region)
    resp = chat.invoke([SystemMessage(content=system), HumanMessage(content=prompt)])
    return str(resp.content).strip()


def _complete_openai(system: str, prompt: str) -> str:
    from openai import OpenAI

    s = get_settings()
    client = OpenAI(base_url=s.openai_base_url) if s.openai_base_url else OpenAI()
    resp = client.chat.completions.create(
        model=s.openai_model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()


def _complete_ollama(system: str, prompt: str) -> str:
    import httpx

    s = get_settings()
    r = httpx.post(
        f"{s.ollama_base_url}/api/chat",
        json={
            "model": s.ollama_model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["message"]["content"].strip()


_BACKENDS = {
    "strands": _complete_strands,
    "bedrock": _complete_bedrock,
    "langchain": _complete_langchain,
    "openai": _complete_openai,
    "ollama": _complete_ollama,
}

# Resolution order per configured provider.
_ORDER = {
    "auto": ("strands", "bedrock"),
    "strands": ("strands",),
    "bedrock": ("bedrock",),
    "langchain": ("langchain",),
    "openai": ("openai",),
    "ollama": ("ollama",),
    "heuristic": (),
}


def complete(system: str, prompt: str) -> str:
    """Return an LLM completion or raise LLMUnavailable."""
    provider = get_settings().llm_provider.lower()
    order = _ORDER.get(provider, ("strands", "bedrock"))

    for backend in order:
        try:
            return _BACKENDS[backend](system, prompt)
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
