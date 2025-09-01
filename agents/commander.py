from typing import Dict, Any, List
from agents.utils import safe_shell, write_incident

def commander_node(approve: bool=False):
    def _run(state: Dict[str, Any]) -> Dict[str, Any]:
        plan = state.get("plan") or []
        actions: List[Dict[str, Any]] = state.get("actions") or []

        # If approval not granted yet, write a preview report and end cleanly.
        if not state.get("approvals", {}).get("approved") and not approve:
            cmds = [p["cmd"] for p in plan if p.get("cmd")]
            # write a preview incident (no actions yet)
            tmp = dict(state)
            tmp["actions"] = actions
            report_path = write_incident(tmp)
            msg = "Dry-run (no approval). Proposed commands:\n" + "\n".join(cmds) + f"\n\nReport written: {report_path}"
            # mark done=True so the graph exits this round
            return {"messages": [{"type": "ai", "content": msg}], "actions": actions, "done": True}

        # Execute allowlisted commands (or dry-run if approve=False)
        for step in plan:
            record = {"step": step}
            if step.get("cmd"):
                out = safe_shell(step["cmd"], approve=approve)
                record["out"] = out
                if step.get("verify"):
                    v = safe_shell(step["verify"], approve=approve)
                    record["verify"] = v
            actions.append(record)

        # Resolve logic
        is_dry = not (state.get("approvals", {}).get("approved")) and not approve
        if is_dry:
            resolved = True
        else:
            resolved = any("200" in (a.get("verify", {}).get("stdout") or "") for a in actions)

        # Write incident report after execution branch
        tmp_state = dict(state)
        tmp_state["actions"] = actions
        report_path = write_incident(tmp_state)

        return {"actions": actions, "done": resolved, "messages": [{"type": "ai", "content": f"Report written: {report_path}"}]}
    return _run
