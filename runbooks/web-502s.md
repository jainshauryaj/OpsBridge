id: web-502s
service: toy-web
diagnostics:
  - "curl -s http://localhost:8080/health"
  - "tail -n 100 logs/toy-web.log"
fixes:
  - cmd: "systemctl restart toy-web"
    verify: "curl -s http://localhost:8080/health"
---
# Web 502s — Runbook
