"""Agent-layer configuration (LLM + ranking weights). DB/embeddings settings
come from epaa_datalake.config (same POSTGRES_*/EMBEDDING_* env)."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    # Orchestrator: custom (hand-rolled v1) | langgraph (v2 graph)
    orchestrator: str = "custom"

    # LLM backend: auto | strands | bedrock | langchain | openai | ollama | heuristic
    llm_provider: str = "auto"
    bedrock_model_id: str = "us.anthropic.claude-opus-4-7-v1:0"
    aws_region: str = "us-east-1"

    # Alternate-framework backends (optional; see providers/llm.py)
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str | None = None  # set for OpenAI-compatible endpoints
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # Skill-Matching / Assignment knobs
    candidate_top_k: int = 15          # how many candidates Skill-Matching shortlists
    relevance_weight: float = 0.6      # weight on semantic + skill relevance
    priority_weight: float = 0.25      # weight on project priority
    availability_weight: float = 0.15  # weight on availability

    # Agents API
    agents_host: str = "0.0.0.0"
    agents_port: int = 8001


@lru_cache
def get_settings() -> AgentSettings:
    return AgentSettings()


# Project priority → numeric weight (used by the Assignment Agent).
PRIORITY_WEIGHTS = {"low": 0.25, "medium": 0.5, "high": 0.8, "critical": 1.0}
# Availability state → factor.
AVAILABILITY_FACTORS = {"available": 1.0, "partially_occupied": 0.6, "unavailable": 0.0}
