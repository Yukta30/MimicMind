from fastapi import FastAPI, Query, Body        # Body added
from fastapi.responses import PlainTextResponse
from typing import Dict                          # NEW
from ..generate.patcher import Patcher
from ..providers.llm import DummyProvider

app = FastAPI()
provider = DummyProvider()
patcher = Patcher(provider)

# (your helpers)
def fetch_ticket_text(key: str):
    return {"key": key, "summary": "Fix pagination", "description": "Boundary bug in Pager"}

def relevant_code_for(ticket):
    return "class Pager:\n    def page(self, items, size):\n        pass\n"

# EXISTING demo endpoint
@app.get("/api/demo/diff", response_class=PlainTextResponse)
def demo_diff(key: str = Query(...), mu: float = Query(0.4)):
    ticket = fetch_ticket_text(key)
    context = relevant_code_for(ticket)
    return patcher.propose_patch(ticket, context, mu=mu, key=key)

# 🔽🔽🔽 PASTE THIS NEW ENDPOINT RIGHT HERE 🔽🔽🔽
@app.post("/api/patch", response_class=PlainTextResponse)
def propose_patch(payload: Dict = Body(...)):
    """
    payload = {
      "ticket": {"key":"WB-1","title":"Add search","description":"..."},
      "files": {"path": "content", ...},
      "mu": 0.4
    }
    """
    ticket = payload.get("ticket") or {"key": "WB-1", "title": "Untitled", "description": ""}
    files: Dict[str, str] = payload.get("files") or {}
    mu = float(payload.get("mu", 0.4))

    # Build a small context string from repo contents
    snippets = []
    for path, content in files.items():
        head = "\n".join(content.splitlines()[:20])  # first 20 lines
        snippets.append(f"### {path}\n{head}")
    context = "\n\n".join(snippets) or "No files"

    # Reuse your existing patcher/provider (they already vary by mu)
    patch = patcher.propose_patch(
        {"key": ticket.get("key"), "summary": ticket.get("title"), "description": ticket.get("description")},
        context,
        mu=mu,
        key=ticket.get("key", "WB-1"),
    )

    return patch or "--- a/empty\n+++ b/empty\n@@\n+No patch generated (demo fallback)\n"
# 🔼🔼🔼 END OF NEW ENDPOINT 🔼🔼🔼
