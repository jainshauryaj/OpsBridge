# agents/fetch_diff.py
from typing import Dict, Any
from services.git_provider import GitProvider

def fetch_diff_node():
    gp = GitProvider(use_shell=False)
    def _run(state: Dict[str, Any]) -> Dict[str, Any]:
        if state.get("diff"):
            return {}
        diff = gp.latest_diff()
        if diff:
            return {"diff": diff, "messages":[{"type":"ai","content":"Fetched latest git diff"}]}
        return {}
    return _run
