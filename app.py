import os, argparse, datetime as dt
from typing import Annotated, TypedDict, List, Dict, Any
from dotenv import load_dotenv
from rich import print as rprint
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
    done: bool
    round: int

def should_bridge_to_code(state: IRState) -> bool:
    if state.get("diff"):
        return True
    for s in (state.get("signals") or []):
        line = (s.get("line") or "") + " " + " ".join(s.get("tags", []))
        if "deploy" in line.lower():
            return True
        if any(tok for tok in line.split() if len(tok) >= 7 and tok.isalnum()):
            return True
    return False

# def resolved_or_loop(state: IRState):
#     return END if state.get("done") else "triage"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--service", default="toy-web")
    ap.add_argument("--approve", action="store_true")
    ap.add_argument("--diff", default="samples/diff.patch")
    args = ap.parse_args()

    model_id = os.getenv("LLM_MODEL", "groq:gemma2-9b-it")
    llm = init_chat_model(model_id, temperature=0)

    retriever = LocalRetriever(persist_path="rag/store/index.pkl", corpus_meta_path="rag/store/corpus.json")

    graph = StateGraph(IRState)
    graph.add_node("triage", triage_node(llm))
    graph.add_node("runbook", runbook_node(llm, retriever))
    graph.add_node("commander", commander_node(approve=args.approve or os.getenv("APPROVE","false").lower()=="true"))
    graph.add_node("static_analyzer", static_analyzer_node())
    graph.add_node("style_guide", style_guide_node(llm, retriever))
    graph.add_node("negotiator", negotiator_node(llm))

    graph.add_edge(START, "triage")
    graph.add_edge("triage", "runbook")
    def after_runbook(state: IRState):
        if should_bridge_to_code(state): return "static_analyzer"
        return "commander"
    graph.add_conditional_edges("runbook", after_runbook)
    graph.add_edge("static_analyzer", "style_guide")
    graph.add_edge("style_guide", "negotiator")
    graph.add_edge("negotiator", "commander")
    # graph.add_conditional_edges("commander", resolved_or_loop)
    graph.add_edge("commander", END)

    app = graph.compile()

    incident_id = f"INC-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    init_state: IRState = {
        "incident": {"id": incident_id, "service": args.service, "started_at": dt.datetime.utcnow().isoformat()+"Z", "severity": "P2"},
        "approvals": {"approved": bool(args.approve)},
        "diff": (open(args.diff, "r", encoding="utf-8").read() if os.path.exists(args.diff) else ""),
        "messages": []
    }
    rprint(f"[bold cyan]Starting incident flow:[/bold cyan] {incident_id}")
    _ = app.invoke(init_state)
    rprint(f"[bold green]Done[/bold green]. See incidents/ for the report.")

if __name__ == "__main__":
    main()
