from fastapi import FastAPI, Query, Body
from fastapi.responses import PlainTextResponse
from typing import Dict
from ..generate.patcher import Patcher
from ..providers.llm import DummyProvider

app = FastAPI()
provider = DummyProvider()
patcher = Patcher(provider)

def fetch_ticket_text(key: str):
    return {"key": key, "summary": "Fix pagination", "description": "Boundary bug in Pager"}

def relevant_code_for(ticket):
    return "class Pager:\n    def page(self, items, size):\n        pass\n"

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/api/demo/diff", response_class=PlainTextResponse)
def demo_diff(key: str = Query(...), mu: float = Query(0.4)):
    ticket = fetch_ticket_text(key)
    context = relevant_code_for(ticket)
    return patcher.propose_patch(ticket, context, mu=mu, key=key)

@app.get("/api/repo/demo")
def repo_demo() -> Dict[str, str]:
    return {
        "src/pager.py": (
            "class Pager:\n"
            "    def page(self, items, size):\n"
            "        pages = []\n"
            "        for i in range(0, len(items)):\n"
            "            if i % size == 0:\n"
            "                pages.append(items[i:i+size])\n"
            "        return pages\n"
        ),
        "src/exporter.py": (
            "class Exporter:\n"
            "    def run(self, items):\n"
            "        for it in items:\n"
            "            self._send(it)\n"
            "    def _send(self, item): ...\n"
        ),
        "README.md": "# Demo repo for MimicMind\n",
    }

@app.post("/api/patch", response_class=PlainTextResponse)
def propose_patch(payload: Dict = Body(...)):
    ticket = payload.get("ticket") or {"key": "WB-1", "title": "Untitled", "description": ""}
    files: Dict[str, str] = payload.get("files") or {}
    mu = float(payload.get("mu", 0.4))

    snippets = []
    for path, content in files.items():
        head = "\n".join(content.splitlines()[:20])
        snippets.append(f"### {path}\n{head}")
    context = "\n\n".join(snippets) or "No files"

    patch = patcher.propose_patch(
        {"key": ticket.get("key"), "summary": ticket.get("title"), "description": ticket.get("description")},
        context,
        mu=mu,
        key=ticket.get("key", "WB-1"),
    )
    return patch or "--- a/empty\n+++ b/empty\n@@\n+No patch generated (demo fallback)\n"
