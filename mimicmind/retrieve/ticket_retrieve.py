from ..ingest.mock_jira import get_ticket
def fetch_ticket_text(key: str) -> str:
    t = get_ticket(key)
    if not t: return f"{key}: (demo) Fix pagination bug"
    return f"{t['key']}: {t['summary']}\n{t.get('description','')}"
