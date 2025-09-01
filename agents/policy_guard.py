# agents/policy_guard.py
import os, yaml, datetime as dt
from typing import Dict, Any, List

DEFAULT_POLICY = {
  "business_hours_block_restart": True,
  "business_hours_tz": "America/New_York",
  "hours_start": 9, "hours_end": 17,  # 9am–5pm
  "require_verify_for_cmds": True,
  "require_rollback_for_restart": True,
  "max_steps": 10
}

def _now_in_tz(tz_str: str):
    # naive UTC -> offset only; keeps it simple for a stub
    return dt.datetime.utcnow()

def load_policy() -> dict:
    path = os.getenv("POLICY_PATH", "policies/policy.yaml")
    if os.path.exists(path):
        try:
            return DEFAULT_POLICY | (yaml.safe_load(open(path)) or {})
        except Exception:
            return DEFAULT_POLICY
    return DEFAULT_POLICY

def check_policy(plan: List[Dict[str, Any]], policy: dict) -> List[str]:
    v: List[str] = []
    if len(plan) > policy["max_steps"]:
        v.append(f"Plan has {len(plan)} steps > max {policy['max_steps']}.")
    # Business hours block (restart)
    now = _now_in_tz(policy["business_hours_tz"])
    hr = now.hour
    bh = policy["business_hours_block_restart"] and (policy["hours_start"] <= hr < policy["hours_end"])
    for step in plan:
        cmd = (step.get("cmd") or "").lower()
        if not cmd: continue
        if policy["require_verify_for_cmds"] and not step.get("verify"):
            v.append(f"Missing verify for cmd: {cmd}")
        if "restart" in cmd and policy["require_rollback_for_restart"] and not step.get("rollback"):
            v.append(f"Missing rollback for restart cmd: {cmd}")
        if bh and "restart" in cmd:
            v.append(f"Restart blocked during business hours: {cmd}")
    return v

def policy_guard_node():
    def _run(state: Dict[str, Any]) -> Dict[str, Any]:
        policy = load_policy()
        plan = state.get("plan") or []
        violations = check_policy(plan, policy)
        updates: Dict[str, Any] = {"policy_violations": violations}
        if violations:
            # block execution; commander will still write preview report
            approvals = dict(state.get("approvals") or {})
            approvals["approved"] = False
            updates["approvals"] = approvals
            updates["messages"] = [{"type":"ai","content":"Policy violations:\n- " + "\n- ".join(violations)}]
        return updates
    return _run
