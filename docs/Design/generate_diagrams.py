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
ACTOR = "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#dae8fc;strokeColor=#6c8ebf;"
CAP = "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;"
TRIGGER = "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontStyle=1;"
NOTE = "shape=note;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;align=left;"
TITLE = "text;html=1;fontSize=18;fontStyle=1;align=left;verticalAlign=middle;"
EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;strokeColor=#475569;"
EDGE_AUTO = "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;strokeColor=#d79b00;dashed=1;"


def node(nid, label, x, y, w, h, style):
    return (nid, label, x, y, w, h, style)


def diagram(name, nodes, edges):
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    for nid, label, x, y, w, h, style in nodes:
        cells.append(
            f'<mxCell id="{nid}" value="{escape(label)}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
        )
    for i, e in enumerate(edges):
        src, tgt, label = e[0], e[1], e[2]
        estyle = e[3] if len(e) > 3 else EDGE
        val = escape(label) if label else ""
        cells.append(
            f'<mxCell id="e{src}_{tgt}_{i}" value="{val}" style="{estyle}" edge="1" parent="1" '
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
    node("o_agents", "Agents (FastAPI)<br>6 MCP-AI agents · Strands+Bedrock", 600, 240, 240, 60, AGENT),
    node("o_datalake", "Datalake (FastAPI)<br>SyntheticData + Airflow DAG", 600, 150, 240, 50, OUTPUT),
    node("o_pg", "Postgres + pgvector<br>(shared schema)", 620, 360, 200, 70, STORE),
    node("o_obs", "Observability<br>Jaeger · Prometheus · Grafana · Kibana", 880, 360, 200, 70, INPUT),
    node("o_airflow", "Airflow (LocalExecutor)", 880, 150, 180, 40, INPUT),
    node("o_mgr", "Project Manager<br>(Admin)", 560, 10, 30, 60, ACTOR),
    node("o_client", "Customer", 660, 10, 30, 60, ACTOR),
]
overall_edges = [
    ("o_mgr", "o_admin", "uses"), ("o_client", "o_cust", "uses"),
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
    node("p_brief", "Project Brief<br>(unstructured text)", 40, 80, 170, 50, INPUT),
    node("p_a1", "1. Requirement Parsing", 240, 80, 180, 40, AGENT),
    node("p_a2", "2. Skill Matching", 240, 140, 180, 40, AGENT),
    node("p_a3", "3. Availability Checker", 240, 200, 180, 40, AGENT),
    node("p_a4", "4. Assignment", 240, 260, 180, 40, AGENT),
    node("p_a5", "5. Communication", 240, 320, 180, 40, AGENT),
    node("p_a6", "6. Reporting", 240, 380, 180, 40, AGENT),
    node("p_alloc", "allocations", 470, 260, 140, 40, OUTPUT),
    node("p_notif", "notifications", 470, 320, 140, 40, OUTPUT),
    node("p_report", "report + metrics", 470, 380, 140, 40, OUTPUT),
    node("p_trace", "agent_runs / agent_steps<br>(persisted trace)", 470, 80, 200, 60, STORE),
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


# ---- Tab: Business Architecture (personas + value stream) ----------------
biz_nodes = [
    t("b_title", "Business Architecture (Personas & Value Stream)", 40, 10),
    # personas (actors)
    node("b_client", "Customer<br>(submits needs)", 60, 70, 30, 60, ACTOR),
    node("b_mgr", "Project / Resource<br>Manager", 300, 70, 30, 60, ACTOR),
    node("b_emp", "Employee /<br>Assignee", 560, 70, 30, 60, ACTOR),
    node("b_exec", "Executive /<br>Management", 820, 70, 30, 60, ACTOR),
    node("b_admin", "Platform /<br>Data Admin", 980, 70, 30, 60, ACTOR),
    # value stream capabilities
    node("b_c1", "Demand Intake<br>(project brief)", 40, 230, 150, 60, CAP),
    node("b_c2", "Requirement<br>Understanding (AI)", 220, 230, 150, 60, AGENT),
    node("b_c3", "Skill & Availability<br>Matching (AI)", 400, 230, 150, 60, AGENT),
    node("b_c4", "Assignment &<br>Approval", 580, 230, 150, 60, CAP),
    node("b_c5", "Communication<br>(notify staff)", 760, 230, 150, 60, CAP),
    node("b_c6", "Reporting &<br>Oversight", 940, 230, 150, 60, CAP),
    node("b_dm", "Data & Workflow<br>Management", 940, 360, 150, 50, CAP),
    node("b_note", "Capabilities 2–3 are fully automated by the LLM agents<br>"
                   "— minimal human intervention (the paper's goal). The manager<br>"
                   "reviews/approves; staff are notified; management gets reports.",
         40, 380, 470, 90, NOTE),
]
biz_edges = [
    ("b_client", "b_c1", "submit brief"),
    ("b_c1", "b_c2", ""), ("b_c2", "b_c3", ""), ("b_c3", "b_c4", ""),
    ("b_c4", "b_c5", ""), ("b_c5", "b_c6", ""),
    ("b_mgr", "b_c4", "review / approve"),
    ("b_emp", "b_c5", "receives"),
    ("b_exec", "b_c6", "consumes"),
    ("b_admin", "b_dm", "runs workflows"),
]

# ---- Tab: Agent Triggers (manual vs automatic) ---------------------------
trig_nodes = [
    t("g_title", "Agent Triggers — Manual vs Automatic", 40, 10),
    node("g_mgr", "Project<br>Manager", 40, 80, 30, 60, ACTOR),
    node("g_monitor", "Admin Portal: Agent Monitor<br>'Run allocation' (MANUAL)", 150, 75, 240, 55, UI),
    node("g_alloc", "allocation-service<br>POST /api/allocations/run", 440, 78, 200, 50, SVC),
    node("g_agents", "Agents pipeline<br>(synchronous, on-demand)", 700, 75, 220, 55, AGENT),

    node("g_admin", "Platform /<br>Data Admin", 40, 230, 30, 60, ACTOR),
    node("g_dm", "Admin Portal: Data Management<br>'Initiate Execution' (MANUAL)", 150, 225, 240, 55, UI),
    node("g_dl", "Datalake API<br>POST /synthetic/generate", 440, 228, 200, 50, SVC),
    node("g_airflow", "Airflow DAG<br>(ASYNC execution)", 700, 228, 200, 50, TRIGGER),
    node("g_pg", "Postgres + pgvector", 700, 330, 200, 45, STORE),

    node("g_note", "MANUAL: a manager/admin triggers from the portal (or any API client).<br>"
                   "ASYNC (dashed): the Datalake API returns immediately and the Airflow DAG<br>"
                   "generates + loads data in the background.<br>"
                   "The 6-agent allocation runs synchronously per request — no scheduled auto-runs<br>"
                   "yet (future: event-driven on brief submission).",
         40, 420, 620, 110, NOTE),
]
trig_edges = [
    ("g_mgr", "g_monitor", "clicks"),
    ("g_monitor", "g_alloc", ""), ("g_alloc", "g_agents", "triggers"),
    ("g_agents", "g_pg", "read/write"),
    ("g_admin", "g_dm", "clicks"),
    ("g_dm", "g_dl", ""),
    ("g_dl", "g_airflow", "async trigger", EDGE_AUTO),
    ("g_airflow", "g_pg", "generate + load", EDGE_AUTO),
]

tabs = [
    diagram("Business Architecture", biz_nodes, biz_edges),
    diagram("Overall Architecture", overall_nodes, overall_edges),
    diagram("Agent Triggers", trig_nodes, trig_edges),
    diagram("Agent Pipeline", pipe_nodes, pipe_edges),
]

tabs.append(agent_tab(
    "Agent 1: Requirement Parsing",
    [("project_briefs.brief_text<br>(free text)", INPUT)],
    "Requirement<br>Parsing Agent",
    "LLM → strict JSON;<br>heuristic fallback:<br>taxonomy match + regex",
    [("parsed_requirements<br>{skills, priority, complexity,<br>duration, headcount}", OUTPUT)],
    [("LLM provider<br>(Strands/Bedrock)", LLM)],
))
tabs.append(agent_tab(
    "Agent 2: Skill Matching",
    [("parsed required_skills", INPUT),
     ("brief.requirements_embedding", INPUT)],
    "Skill<br>Matching Agent",
    "pgvector cosine distance<br>+ skill overlap<br>blend → relevance",
    [("ranked candidates<br>[relevance score]", OUTPUT)],
    [("employees.profile_embedding<br>(pgvector)", STORE)],
))
tabs.append(agent_tab(
    "Agent 3: Availability Checker",
    [("candidates", INPUT),
     ("employees.availability_state", INPUT)],
    "Availability<br>Checker Agent",
    "DB-only;<br>drop 'unavailable';<br>set availability_factor",
    [("available candidates", OUTPUT),
     ("metric: conflicts_avoided", OUTPUT)],
    [],
))
tabs.append(agent_tab(
    "Agent 4: Assignment",
    [("available candidates", INPUT),
     ("project priority weight", INPUT)],
    "Assignment<br>Agent",
    "score = w_rel·relevance<br>+ w_pri·priority<br>+ w_avail·availability;<br>rank → top headcount",
    [("allocations (persisted)<br>+ rationale", OUTPUT)],
    [],
))
tabs.append(agent_tab(
    "Agent 5: Communication",
    [("assignments", INPUT)],
    "Communication<br>Agent",
    "template subject/body;<br>queue per assignee",
    [("notifications rows<br>(channel: log)", OUTPUT)],
    [],
))
tabs.append(agent_tab(
    "Agent 6: Reporting",
    [("run context + metrics", INPUT)],
    "Reporting<br>Agent",
    "LLM summary;<br>template fallback",
    [("reports row<br>summary + metrics_json", OUTPUT)],
    [("LLM provider<br>(Strands/Bedrock)", LLM)],
))

xml = '<mxfile host="app.diagrams.net" type="device">' + "".join(tabs) + "</mxfile>"

out = Path(__file__).parent / "epaa-architecture.drawio"
out.write_text(xml, encoding="utf-8")
print(f"wrote {out} ({len(tabs)} tabs, {len(xml)} bytes)")
