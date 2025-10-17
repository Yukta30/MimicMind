from pathlib import Path
import json
DATA = Path("data/demo/tickets.jsonl")
def list_tickets(limit: int = 50):
    if not DATA.exists(): return []
    out = []
    for i, line in enumerate(DATA.read_text(encoding="utf-8").splitlines()):
        if i >= limit: break
        out.append(json.loads(line))
    return out
def get_ticket(key: str) -> dict | None:
    for line in DATA.read_text(encoding="utf-8").splitlines():
        j = json.loads(line)
        if j.get("key")==key: return j
    return None
