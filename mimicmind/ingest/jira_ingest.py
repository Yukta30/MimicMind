import os, requests
JIRA = lambda p: f"{os.getenv('JIRA_BASE_URL','')}/rest/api/3/{p}"
AUTH = (os.getenv("JIRA_EMAIL",""), os.getenv("JIRA_API_TOKEN",""))
def get_issue(key: str) -> dict:
    r = requests.get(JIRA(f"issue/{key}"), auth=AUTH)
    r.raise_for_status()
    return r.json()
