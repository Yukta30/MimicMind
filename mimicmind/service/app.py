from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse
from ..generate.patcher import Patcher
from ..providers.llm import DummyProvider
from fastapi import Body
from typing import Dict


app = FastAPI()
provider = DummyProvider()
patcher = Patcher(provider)

def fetch_ticket_text(key: str):
    # minimal stub for demo
    return {"key": key, "summary": "Fix pagination", "description": "Boundary bug in Pager"}

def relevant_code_for(ticket):
    # pretend context snippet
    return "class Pager:\n    def page(self, items, size):\n        pass\n"

@app.get("/api/demo/diff", response_class=PlainTextResponse)
def demo_diff(key: str = Query(...), mu: float = Query(0.4)):
    ticket = fetch_ticket_text(key)
    context = relevant_code_for(ticket)
    # IMPORTANT: pass mu into the provider via patcher
    return patcher.propose_patch(ticket, context, mu=mu, key=key)

@app.get("/api/repo/demo")
def repo_demo() -> Dict[str, str]:
    """
    Tiny in-memory repo so the workbench can show files.
    Replace with your own files later if you want.
    """
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
        "README.md": "# Demo repo for MimicMind\\n",
    }
