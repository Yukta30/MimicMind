import requests, os
GITHUB_API = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept":"application/vnd.github+json"}
def open_pr(owner: str, repo: str, head_branch: str, base_branch: str, title: str, body: str):
    url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls"
    r = requests.post(url, headers=HEADERS, json={
        "title": title, "head": head_branch, "base": base_branch, "body": body
    })
    r.raise_for_status()
    return r.json()
