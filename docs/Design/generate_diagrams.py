#!/usr/bin/env python3
"""Generate the multi-tab draw.io architecture file (epaa-architecture.drawio).

Tabs: Overall Architecture, Agent Pipeline, and one per MCP-AI agent.
Run: `python3 docs/Design/generate_diagrams.py` (no dependencies).
Open the .drawio in https://app.diagrams.net or the VS Code Draw.io extension.
"""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

# ---- styles ---------------------------------------------------------------
INPUT = "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
AGENT = "rounded=1;whiteSpace=wrap;html=1;fillColor=#4f46e5;strokeColor=#3730a3;fontColor=#ffffff;fontStyle=1;"
OUTPUT = "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;"
STORE = "shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;"
LLM = "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;"
SVC = "rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;"
UI = "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;"
TITLE = "text;html=1;fontSize=18;fontStyle=1;align=left;verticalAlign=middle;"
EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;strokeColor=#475569;"


def node(nid, label, x, y, w, h, style):
    return (nid, label, x, y, w, h, style)


def diagram(name, nodes, edges):
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    for nid, label, x, y, w, h, style in nodes:
        cells.append(
            f'<mxCell id="{nid}" value="{escape(label)}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
        )
    for i, (src, tgt, label) in enumerate(edges):
        val = escape(label) if label else ""
        cells.append(
            f'<mxCell id="e{src}_{tgt}_{i}" value="{val}" style="{EDGE}" edge="1" parent="1" '
            f'source="{src}" target="{tgt}"><mxGeometry relative="1" as="geometry"/></mxCell>'
        )
    body = "".join(cells)
    return (
        f'<diagram id="{name.replace(" ", "_")}" name="{escape(name)}">'
        f'<mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" '
        f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
        f'pageWidth="1100" pageHeight="700" math="0" shadow="0"><root>{body}</root></mxGraphModel></diagram>'
    )


def t(nid, label, x, y):
    return node(nid, label, x, y, 320, 30, TITLE)


# ---- Tab 1: Overall architecture -----------------------------------------
overall_nodes = [
    t("o_title", "EPAA — Overall Architecture", 40, 10),
    node("o_admin", "Admin Portal (Angular 18)", 60, 70, 200, 50, UI),
    node("o_cust", "Projects Portal (Angular 18)", 300, 70, 200, 50, UI),
    node("o_gw", "API Gateway (Spring Cloud Gateway)", 120, 160, 320, 50, SVC),
    node("o_emp", "employee-service", 40, 250, 150, 40, SVC),
    node("o_prj", "project-service", 200, 250, 150, 40, SVC),
    node("o_alloc", "allocation-service", 360, 250, 150, 40, SVC),
    node("o_notif", "notification-service", 40, 300, 150, 40, SVC),
    node("o_rep", "reporting-service", 200, 300, 150, 40, SVC),
    node("o_agents", "Agents (FastAPI)&lt;br&gt;6 MCP-AI agents · Strands+Bedrock", 600, 240, 240, 60, AGENT),
    node("o_datalake", "Datalake (FastAPI)&lt;br&gt;SyntheticData + Airflow DAG", 600, 150, 240, 50, OUTPUT),
    node("o_pg", "Postgres + pgvector&lt;br&gt;(shared schema)", 620, 360, 200, 70, STORE),
    node("o_obs", "Observability&lt;br&gt;Jaeger · Prometheus · Grafana · Kibana", 880, 360, 200, 70, INPUT),
    node("o_airflow", "Airflow (LocalExecutor)", 880, 150, 180, 40, INPUT),
]
overall_edges = [
    ("o_admin", "o_gw", ""), ("o_cust", "o_gw", ""),
    ("o_gw", "o_emp", ""), ("o_gw", "o_prj", ""), ("o_gw", "o_alloc", ""),
    ("o_gw", "o_notif", ""), ("o_gw", "o_rep", ""),
    ("o_alloc", "o_agents", "POST /allocations/run"),
    ("o_agents", "o_pg", "read/write"),
    ("o_datalake", "o_pg", "seed"),
    ("o_datalake", "o_airflow", "trigger DAG"),
    ("o_emp", "o_pg", ""), ("o_prj", "o_pg", ""), ("o_rep", "o_pg", ""),
    ("o_agents", "o_obs", "OTel"),
]

# ---- Tab 2: Agent pipeline ------------------------------------------------
pipe_nodes = [
    t("p_title", "Agent Pipeline (Orchestrator)", 40, 10),
    node("p_brief", "Project Brief&lt;br&gt;(unstructured text)", 40, 80, 170, 50, INPUT),
    node("p_a1", "1. Requirement Parsing", 240, 80, 180, 40, AGENT),
    node("p_a2", "2. Skill Matching", 240, 140, 180, 40, AGENT),
    node("p_a3", "3. Availability Checker", 240, 200, 180, 40, AGENT),
    node("p_a4", "4. Assignment", 240, 260, 180, 40, AGENT),
    node("p_a5", "5. Communication", 240, 320, 180, 40, AGENT),
    node("p_a6", "6. Reporting", 240, 380, 180, 40, AGENT),
    node("p_alloc", "allocations", 470, 260, 140, 40, OUTPUT),
    node("p_notif", "notifications", 470, 320, 140, 40, OUTPUT),
    node("p_report", "report + metrics", 470, 380, 140, 40, OUTPUT),
    node("p_trace", "agent_runs / agent_steps&lt;br&gt;(persisted trace)", 470, 80, 200, 60, STORE),
    node("p_pg", "Postgres + pgvector", 700, 200, 180, 50, STORE),
]
pipe_edges = [
    ("p_brief", "p_a1", ""),
    ("p_a1", "p_a2", "parsed reqs"), ("p_a2", "p_a3", "candidates"),
    ("p_a3", "p_a4", "available"), ("p_a4", "p_a5", "assignments"),
    ("p_a5", "p_a6", ""),
    ("p_a4", "p_alloc", ""), ("p_a5", "p_notif", ""), ("p_a6", "p_report", ""),
    ("p_a1", "p_trace", "step"), ("p_a6", "p_trace", "step"),
    ("p_a2", "p_pg", "pgvector"), ("p_alloc", "p_pg", ""),
]


def agent_tab(name, inputs, agent_label, logic, outputs, extras):
    """Standard left→right agent diagram."""
    pre = name.split(":")[-1].strip().replace(" ", "")[:6]
    nodes = [t(f"{pre}_title", name, 40, 10)]
    edges = []
    ay = 120
    nodes.append(node(f"{pre}_agent", agent_label, 360, ay, 220, 80, AGENT))
    for i, (lab, sty) in enumerate(inputs):
        nid = f"{pre}_in{i}"
        nodes.append(node(nid, lab, 40, 80 + i * 70, 230, 50, sty))
        edges.append((nid, f"{pre}_agent", ""))
    for i, (lab, sty) in enumerate(outputs):
        nid = f"{pre}_out{i}"
        nodes.append(node(nid, lab, 660, 80 + i * 70, 230, 50, sty))
        edges.append((f"{pre}_agent", nid, ""))
    for i, (lab, sty) in enumerate(extras):
        nid = f"{pre}_ex{i}"
        nodes.append(node(nid, lab, 360, 240 + i * 70, 220, 50, sty))
        edges.append((f"{pre}_agent", nid, ""))
    nodes.append(node(f"{pre}_logic", logic, 360, 240 + len(extras) * 70, 220, 110, INPUT))
    return diagram(name, nodes, edges)


tabs = [diagram("Overall Architecture", overall_nodes, overall_edges),
        diagram("Agent Pipeline", pipe_nodes, pipe_edges)]

tabs.append(agent_tab(
    "Agent 1: Requirement Parsing",
    [("project_briefs.brief_text&lt;br&gt;(free text)", INPUT)],
    "Requirement&lt;br&gt;Parsing Agent",
    "LLM → strict JSON;&lt;br&gt;heuristic fallback:&lt;br&gt;taxonomy match + regex",
    [("parsed_requirements&lt;br&gt;{skills, priority, complexity,&lt;br&gt;duration, headcount}", OUTPUT)],
    [("LLM provider&lt;br&gt;(Strands/Bedrock)", LLM)],
))
tabs.append(agent_tab(
    "Agent 2: Skill Matching",
    [("parsed required_skills", INPUT),
     ("brief.requirements_embedding", INPUT)],
    "Skill&lt;br&gt;Matching Agent",
    "pgvector cosine distance&lt;br&gt;+ skill overlap&lt;br&gt;blend → relevance",
    [("ranked candidates&lt;br&gt;[relevance score]", OUTPUT)],
    [("employees.profile_embedding&lt;br&gt;(pgvector)", STORE)],
))
tabs.append(agent_tab(
    "Agent 3: Availability Checker",
    [("candidates", INPUT),
     ("employees.availability_state", INPUT)],
    "Availability&lt;br&gt;Checker Agent",
    "DB-only;&lt;br&gt;drop 'unavailable';&lt;br&gt;set availability_factor",
    [("available candidates", OUTPUT),
     ("metric: conflicts_avoided", OUTPUT)],
    [],
))
tabs.append(agent_tab(
    "Agent 4: Assignment",
    [("available candidates", INPUT),
     ("project priority weight", INPUT)],
    "Assignment&lt;br&gt;Agent",
    "score = w_rel·relevance&lt;br&gt;+ w_pri·priority&lt;br&gt;+ w_avail·availability;&lt;br&gt;rank → top headcount",
    [("allocations (persisted)&lt;br&gt;+ rationale", OUTPUT)],
    [],
))
tabs.append(agent_tab(
    "Agent 5: Communication",
    [("assignments", INPUT)],
    "Communication&lt;br&gt;Agent",
    "template subject/body;&lt;br&gt;queue per assignee",
    [("notifications rows&lt;br&gt;(channel: log)", OUTPUT)],
    [],
))
tabs.append(agent_tab(
    "Agent 6: Reporting",
    [("run context + metrics", INPUT)],
    "Reporting&lt;br&gt;Agent",
    "LLM summary;&lt;br&gt;template fallback",
    [("reports row&lt;br&gt;summary + metrics_json", OUTPUT)],
    [("LLM provider&lt;br&gt;(Strands/Bedrock)", LLM)],
))

xml = '<mxfile host="app.diagrams.net" type="device">' + "".join(tabs) + "</mxfile>"

out = Path(__file__).parent / "epaa-architecture.drawio"
out.write_text(xml, encoding="utf-8")
print(f"wrote {out} ({len(tabs)} tabs, {len(xml)} bytes)")
