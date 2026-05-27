# Alternate framework adapters (M9) & orchestration (M12)

Two independent switches: **`LLM_PROVIDER`** (which LLM framework makes a completion)
and **`ORCHESTRATOR`** (how the 6 agents are sequenced).

## Orchestration — `ORCHESTRATOR`

| Value | Implementation | Notes |
|-------|----------------|-------|
| `custom` (default) | `orchestrator.py` — hand-rolled sequential pipeline (v1) | no extra deps; always available |
| `langgraph` | `orchestrator_langgraph.py` — LangGraph `StateGraph` (v2) | needs the `langgraph` extra; reuses the **same 6 agent classes** |

Both persist the same `agent_runs`/`agent_steps` trace and return the same response
shape (v2 adds `"orchestrator": "langgraph"`). `runner.py` selects at runtime and falls
back to `custom` if `langgraph` isn't installed. The v2 graph also adds a **conditional
edge**: if the Availability Checker leaves no available candidates, it skips Assignment
+ Communication and routes straight to Reporting — something the linear v1 can't express
as cleanly. Switch with `ORCHESTRATOR=langgraph` (install `pip install '.[langgraph]'`).

## LLM backends — `LLM_PROVIDER`

The agents reason through a single `complete(system, prompt)` interface
(`Middleware/Agents/src/epaa/providers/llm.py`), so the underlying framework is a
config switch (`LLM_PROVIDER`). Every backend import is guarded — an unavailable
backend falls back to the deterministic heuristic, so the pipeline always runs.

| Adapter | `LLM_PROVIDER` | Status | Install |
|---------|----------------|--------|---------|
| Strands Agents + Bedrock | `strands` / `auto` | implemented | `pip install '.[strands]'` |
| Bedrock (boto3 direct) | `bedrock` | implemented | base deps |
| LangChain (langchain-aws) | `langchain` | implemented | `pip install '.[langchain]'` |
| OpenAI SDK (or compatible) | `openai` | implemented | `pip install '.[openai]'` |
| HuggingFace local via Ollama | `ollama` | implemented | run Ollama; `OLLAMA_MODEL=…` |
| heuristic (offline) | `heuristic` | implemented | base deps |

All six resolve through `_BACKENDS` / `_ORDER` and are covered by
`tests/test_providers.py` (offline). Switch with one env var, e.g.:

```bash
LLM_PROVIDER=langchain epaa-agents run --any
LLM_PROVIDER=openai OPENAI_API_KEY=sk-… epaa-agents run --any
LLM_PROVIDER=ollama OLLAMA_MODEL=llama3.1 epaa-agents run --any
```

## Embeddings

`EMBEDDING_PROVIDER` similarly swaps Titan (`bedrock`), HuggingFace MiniLM (`hf`,
via `sentence-transformers`), or the offline deterministic `hash` fallback
(`Middleware/Datalake/.../generators/embeddings.py`).

## Java alternate path — Spring AI (9.3)

For an all-Java agent demo, `allocation-service` can call an LLM directly via
**Spring AI** instead of delegating to the Python Agents service. Add
`spring-ai-bedrock-converse-spring-boot-starter`, inject a `ChatClient`, and have
the Requirement-Parsing / Reporting steps use it. Kept as a documented alternate so
the primary path stays Python/Strands (per the locked stack decision); enable it as
a Spring profile when exploring Spring AI.

## SageMaker-hosted model (9.5)

The `sagemaker` Terraform module provisions a Studio domain + execution role. To use
a self-hosted HuggingFace model as a Bedrock alternate, deploy it to a SageMaker
real-time endpoint and add a `sagemaker` backend to `providers/llm.py` that invokes
the endpoint (boto3 `sagemaker-runtime`). Requires a live AWS account, so it is wired
as a deployment option rather than run here.
