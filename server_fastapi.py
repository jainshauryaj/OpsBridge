# server_fastapi.py
from fastapi import FastAPI
from pydantic import BaseModel
from runner import run_once

app = FastAPI(title="OpsBridge API", version="0.1.0")

class RunReq(BaseModel):
    service: str = "toy-web"
    approve: bool = False
    diff_path: str | None = None

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/run")
def run(req: RunReq):
    report_path, incident_id = run_once(service=req.service, approve=req.approve, diff_path=req.diff_path)
    return {"ok": True, "incident_id": incident_id, "report_path": report_path}
