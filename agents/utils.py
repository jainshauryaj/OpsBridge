import os
from typing import List, Dict, Any
ALLOWLIST = {"tail -n 200 logs/toy-web.log","tail -n 100 logs/toy-web.log","curl -s http://localhost:8080/health","systemctl restart toy-web","systemctl status toy-web"}
def safe_shell(cmd: str, approve: bool=False) -> Dict[str, Any]:
    import subprocess, shlex
    if cmd not in ALLOWLIST: return {"stdout":"", "stderr":f"Command not allowed: {cmd}", "code":127}
    if not approve: return {"stdout": f"[dry-run] {cmd}", "stderr":"", "code": 0}
    try:
        p = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=10)
        return {"stdout": p.stdout, "stderr": p.stderr, "code": p.returncode}
    except Exception as e:
        return {"stdout":"", "stderr": str(e), "code": 1}
def parse_signals_from_log(text: str) -> List[Dict[str, Any]]:
    signals = []
    for line in text.splitlines():
        tags = []
        if "502" in line: tags.append("HTTP_502")
        if "deploy" in line.lower(): tags.append("DEPLOY")
        signals.append({"line": line.strip(), "tags": tags})
    return signals
def render_incident_report(state: Dict[str, Any]) -> str:
    inc = state.get("incident", {})
    lines = [f"# Incident {inc.get('id','')} — {inc.get('service','')}","","## Symptoms"]
    for s in (state.get("signals") or [])[:20]:
        lines.append(f"- {s.get('line','')}")
    lines += ["","## Plan"]
    for i, step in enumerate(state.get('plan') or [], 1):
        lines.append(f"{i}. {step.get('step','')}")
    lines += ["","## Actions"]
    for a in (state.get('actions') or []):
        st = a.get('step',{})
        lines.append(f"- {st.get('step','')}")
        out = a.get('out',{})
        if out: lines += ["  ```", (out.get('stdout') or '')[:600], "  ```"]
    return "\n".join(lines)
def write_incident(state: Dict[str, Any]) -> str:
    os.makedirs("incidents", exist_ok=True)
    inc_id = state.get("incident", {}).get("id", "INC-unknown")
    path = f"incidents/{inc_id}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(render_incident_report(state))
    return path
