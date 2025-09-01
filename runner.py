# runner.py
import os, datetime as dt
from typing import Annotated, TypedDict, List, Dict, Any
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain.chat_models import init_chat_model

from agents.triage import triage_node
from agents.runbook import runbook_node
from agents.commander import commander_node
from agents.static_analyzer import static_analyzer_node
from agents.style_guide import style_guide_node
from agents.negotiator import negotiator_node
from agents.policy_guard import policy_guard_node
from agents.fetch_diff import fetch_diff_node
from rag.retriever import LocalRetriever

load_dotenv()

class IRState(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    incident: Dict[str, Any]
    signals: List[Dict[str, Any]]
    hypotheses: List[str]
    plan: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    approvals: Dict[str, bool]
    diff: str
    review: Dict[str, Any]
    policy_violations: List[str]
    done: bool
    round: int

def build_graph(model_id: str, approve: bool):
    llm = init_chat_model(model_id, temperature=0)
    retriever = LocalRetriever(persist_path="rag/store/index.pkl", corpus_meta_path="rag/store/corpus.json")

    g = StateGraph(IRState)
    # Nodes
    g.add_node("triage", triage_node(llm))
    g.add_node("fetch_diff", fetch_diff_node())                # NEW
    g.add_node("runbook", runbook_node(llm, retriever))
    g.add_node("static_analyzer", static_analyzer_node())
    g.add_node("style_guide", style_guide_node(llm, retriever))
    g.add_node("negotiator", negotiator_node(llm))
    g.add_node("policy_guard", policy_guard_node())            # NEW
    g.add_node("commander", commander_node(approve=approve))

    # Edges
    g.add_edge(START, "triage")
    g.add_edge("triage", "fetch_diff")                         # triage → fetch diff → runbook
    g.add_edge("fetch_diff", "runbook")

    def should_bridge_to_code(state: IRState) -> str:
        if state.get("diff"):
            return "static_analyzer"
        # if logs mention deploy/sha, prefer code path
        for s in (state.get("signals") or []):
            line = (s.get("line") or "").lower()
            if "deploy" in line: return "static_analyzer"
        return "policy_guard"

    g.add_conditional_edges("runbook", should_bridge_to_code)
    g.add_edge("static_analyzer", "style_guide")
    g.add_edge("style_guide", "negotiator")
    g.add_edge("negotiator", "policy_guard")
    g.add_edge("policy_guard", "commander")
    g.add_edge("commander", END)                               # always end after commander

    return g.compile()

def run_once(service: str = "toy-web", approve: bool = False, diff_path: str | None = None):
    model_id = os.getenv("LLM_MODEL", "groq:gemma2-9b-it")
    app = build_graph(model_id, approve)

    incident_id = f"INC-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    diff = ""
    if diff_path and os.path.exists(diff_path):
        diff = open(diff_path, "r", encoding="utf-8").read()

    state: IRState = {
        "incident": {"id": incident_id, "service": service, "started_at": dt.datetime.utcnow().isoformat()+"Z", "severity": "P2"},
        "approvals": {"approved": approve},
        "diff": diff,
        "messages": []
    }
    out = app.invoke(state)
    return f"incidents/{incident_id}.md", incident_id
