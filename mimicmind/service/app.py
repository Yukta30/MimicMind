from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse
from ..generate.patcher import Patcher
from ..providers.llm import DummyProvider

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
