from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from .jira_webhook import router as jira_router
from ..generate.patcher import Patcher
from ..retrieve.ticket_retrieve import fetch_ticket_text
from ..retrieve.code_retrieve import relevant_code_for

app = FastAPI(title="MimicMind")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(jira_router)

patcher = Patcher()

@app.get("/api/demo/diff")
def demo_diff(key: str = Query(...), mu: float = Query(0.4)):
    ticket = fetch_ticket_text(key)
    context = relevant_code_for(ticket)
    return patcher.propose_patch(ticket, context)

@app.get("/health")
def health():
    return {"ok": True, "mode": "demo"}
