# Design diagrams

`epaa-architecture.drawio` — a multi-tab [draw.io](https://app.diagrams.net)
(diagrams.net) file. Open it in the web app or the VS Code **Draw.io Integration**
extension.

## Tabs

1. **Overall Architecture** — portals → gateway → microservices → Agents/Datalake → Postgres + observability
2. **Agent Pipeline** — the orchestrator running the 6 agents in sequence + persisted trace
3. **Agent 1: Requirement Parsing**
4. **Agent 2: Skill Matching**
5. **Agent 3: Availability Checker**
6. **Agent 4: Assignment**
7. **Agent 5: Communication**
8. **Agent 6: Reporting**

Legend: blue = input · indigo = agent · green = output · grey cylinder = data store ·
amber = LLM provider · purple = Spring service · yellow = Angular portal.

## Regenerate

```bash
python3 docs/Design/generate_diagrams.py   # no dependencies
```

Edit `generate_diagrams.py` (the source of truth) and re-run, or edit the
`.drawio` directly in diagrams.net.
