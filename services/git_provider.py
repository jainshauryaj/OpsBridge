# services/git_provider.py
import os, subprocess, shlex

class GitProvider:
    def __init__(self, use_shell: bool = True):
        self.use_shell = use_shell

    def _run(self, cmd: str) -> str:
        p = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=10)
        if p.returncode != 0:
            return ""
        return p.stdout

    def latest_diff(self, spec: str = "HEAD~1..HEAD") -> str:
        if self.use_shell:
            return self._run(f"git diff -U0 {spec}")
        return ""  # MCP client path would go here
