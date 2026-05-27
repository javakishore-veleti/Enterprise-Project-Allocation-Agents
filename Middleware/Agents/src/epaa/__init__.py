"""EPAA Agents — the six MCP-AI autonomous agents and their orchestrator.

1. Requirement Parsing  2. Skill Matching  3. Availability Checker
4. Assignment           5. Communication   6. Reporting

LLM-driven agents use Strands + Bedrock when available and fall back to
deterministic heuristics so the pipeline runs offline. Shared schema, DB session
and embeddings come from the `epaa_datalake` package (the data layer).
"""

__version__ = "0.1.0"
