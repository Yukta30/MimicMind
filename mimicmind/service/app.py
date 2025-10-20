from fastapi import FastAPI, Query, Body
from fastapi.responses import PlainTextResponse
from typing import Dict
from ..generate.patcher import Patcher
from ..providers.llm import DummyProvider

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["https://mimicmind-4.onrender.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

from fastapi import UploadFile, File, Form
import zipfile, io

ACCEPT_EXT = ('.py','.ts','.tsx','.js','.jsx','.json','.md',
              '.go','.java','.rb','.rs','.cpp','.c','.cs','.php','.kt','.swift')

def _wanted(name: str) -> bool:
    n = name.lower()
    if n.endswith('/'): return False
    if '/.git/' in n or n.startswith('.git/'): return False
    if '/node_modules/' in n: return False
    if '/build/' in n or '/dist/' in n: return False
    return any(n.endswith(ext) for ext in ACCEPT_EXT)

@app.post("/api/patch-zip", response_class=PlainTextResponse)
async def propose_patch_zip(
    file: UploadFile = File(...),
    mu: float = Form(0.4),
    key: str = Form('WB-1'),
    title: str = Form('Untitled'),
    description: str = Form(''),
):
    data = await file.read()
    z = zipfile.ZipFile(io.BytesIO(data))
    files: Dict[str, str] = {}
    for name in z.namelist():
        if not _wanted(name): continue
        try:
            raw = z.read(name)
            text = raw.decode('utf-8', errors='ignore')
        except Exception:
            continue
        files[name] = text

    snippets = []
    for path, content in files.items():
        head = "\n".join(content.splitlines()[:20])
        snippets.append(f"### {path}\n{head}")
    context = "\n\n".join(snippets) or "No files"

    patch = patcher.propose_patch(
        {"key": key, "summary": title, "description": description},
        context,
        mu=mu,
        key=key,
    )
    return patch or "--- a/empty\n+++ b/empty\n@@\n+No patch generated (demo fallback)\n"


import io, zipfile
from fastapi import UploadFile, File, Form
from fastapi.responses import JSONResponse

ACCEPT_EXT = {".py",".ts",".tsx",".js",".jsx",".json",".md",".go",".java",
              ".rb",".rs",".cpp",".c",".cs",".php",".kt",".swift"}

def _keep(path: str) -> bool:
    p = path.lower()
    if "node_modules/" in p or "/build/" in p or "/dist/" in p: return False
    if p.startswith(".git/") or "/.git/" in p: return False
    return any(p.endswith(ext) for ext in ACCEPT_EXT)

@app.post("/api/patch-zip-json")
async def patch_zip_json(
    file: UploadFile = File(...),
    key: str = Form("WB-1"),
    title: str = Form("Upload"),
    description: str = Form(""),
    mu: float = Form(0.4),
):
    data = await file.read()
    zf = zipfile.ZipFile(io.BytesIO(data))
    files: dict[str, str] = {}
    for name in zf.namelist():
        if _keep(name):
            try:
                files[name] = zf.read(name).decode("utf-8", "ignore")
            except Exception:
                pass

    # Build short context from the uploaded repo
    heads = []
    for path, content in list(files.items())[:80]:  # avoid giant payloads
        lines = content.splitlines()
        heads.append(f"### {path}\n" + "\n".join(lines[:20]))
    context = "\n\n".join(heads) or "No files"

    ticket = {"key": key, "summary": title, "description": description}
    diff = patcher.propose_patch(ticket, context, mu=mu, key=key) or ""

    return JSONResponse({"diff": diff, "files": files})

