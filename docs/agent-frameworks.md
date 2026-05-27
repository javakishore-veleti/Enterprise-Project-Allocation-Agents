# Multi-agent orchestration frameworks

Reference landscape (early 2026) for agentic frameworks, and how they relate to
this project. A condensed version lives in the [README](../README.md#multi-agent-orchestration-frameworks);
this is the fuller writeup.

The agents here reason through one swappable `complete()` interface
(`Middleware/Agents/src/epaa/providers/llm.py`), so the LLM framework is a config
switch (`LLM_PROVIDER`); the *orchestration* is a separate switch (`ORCHESTRATOR`).

## Code-first frameworks (Python-centric)

| Framework | Owner | Orchestration model | Best for |
|-----------|-------|---------------------|----------|
| **LangGraph** | LangChain | Stateful graph (nodes/edges, cycles, checkpointing, interrupts) | Complex, controllable multi-agent flows; durable/resumable state, human-in-the-loop |
| **CrewAI** | CrewAI | Role-based "crews" + tasks (sequential/hierarchical) | Quick role-playing agent teams; opinionated, batteries-included |
| **OpenAI Agents SDK** | OpenAI | Lightweight handoffs + guardrails + sessions | OpenAI-model apps; simple, production-minded (successor to Swarm) |
| **Microsoft Agent Framework** | Microsoft | AutoGen group-chat + Semantic Kernel planners/plugins | Enterprise .NET/Python; was AutoGen/AG2 + SK |
| **Strands Agents** | AWS | Model-driven agent loop + tools + multi-agent | AWS/Bedrock-native, lightweight (this repo's designated default) |
| **Google ADK** (Agent Dev Kit) | Google | Hierarchical agents + A2A interop | Gemini/Vertex; multi-agent-as-a-service |
| **LlamaIndex Workflows / AgentWorkflow** | LlamaIndex | Event-driven workflows | RAG-heavy agent apps |
| **Pydantic AI** | Pydantic | Type-safe agents + graphs | Strongly-typed, testable agents |
| **Haystack** | deepset | Pipelines + agents | RAG + production search |
| **Agno** (ex-Phidata), **Atomic Agents** | community | Lightweight agent teams | Minimal, fast prototyping |

## Managed / platform offerings

- **Amazon Bedrock Agents** (+ multi-agent collaboration: supervisor/sub-agents) — AWS managed
- **Vertex AI Agent Builder / Agent Engine** — Google managed
- **Azure AI Foundry Agent Service** — Microsoft managed
- **LangGraph Platform** (LangSmith) — hosting + observability for LangGraph graphs

## Cross-cutting protocols (interop, not orchestrators themselves)

- **MCP (Model Context Protocol)** — Anthropic; standardizes tools/context exposure (the
  "MCP" this repo deliberately did *not* name itself after)
- **A2A (Agent2Agent)** — Google-led; agent-to-agent communication across frameworks

## How this maps to this project

- **Default**: Strands Agents on Bedrock (designated), with **LangChain**, **OpenAI SDK**,
  and **Ollama/HF** wired as swappable LLM backends — see [adapters.md](adapters.md).
- **Orchestration**:
  - `ORCHESTRATOR=custom` (default) — a hand-rolled sequential pipeline (v1).
  - `ORCHESTRATOR=langgraph` (v2) — a LangGraph `StateGraph` reusing the same 6 agent
    classes, with a conditional edge, **streaming** live trace, and **human-in-the-loop
    approval** before assignment is finalized.

## Choosing one (rules of thumb)

- **Deterministic, ordered pipeline with state + approvals** → LangGraph (this project's v2).
- **Role-playing teams, fast** → CrewAI.
- **OpenAI-first, minimal** → OpenAI Agents SDK.
- **Stay all-AWS / Bedrock-native** → Strands (or Bedrock Agents managed).
- **All-Java / Spring shop** → Spring AI or Microsoft Agent Framework.
- **Heavy retrieval** → LlamaIndex or Haystack.
