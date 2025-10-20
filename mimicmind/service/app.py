# mimicmind/service/app.py
from __future__ import annotations

import io
import zipfile
from typing import Dict

from fastapi import FastAPI, UploadFile, File, Form, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse

# Your existing patcher/provider
from ..generate.patcher import Patcher
from ..providers.llm import DummyProvider  # swap with a real provider when ready

app = FastAPI(title="MimicMind API")

# --- CORS so your Next.js frontend can call us in the browser ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # tighten to your web origin if you want
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

provider = DummyProvider()
patcher = Patcher(provider)

# ---------- helpers ----------

ACCEPT_EXT = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md",
    ".go", ".java", ".rb", ".rs", ".cpp", ".c", ".cs", ".php", ".kt", ".swift",
}

def _keep(path: str) -> bool:
    p = path.lower()
    if "node_modules/" in p or "/build/" in p or "/dist/" in p:
        return False
    if p.startswith(".git/") or "/.git/" in p:
        return False
    return any(p.endswith(ext) for ext in ACCEPT_EXT)

def _context_from_files(files: Dict[str, str], head_lines: int = 20, max_files: int = 80) -> str:
    """
    Build a small context string for the LLM by concatenating the first N lines
    of up to M files. This keeps context light but style-rich.
    """
    heads = []
    for i, (path, content) in enumerate(files.items()):
        if i >= max_files:
            break
        lines = content.splitlines()
        heads.append(f"### {path}\n" + "\n".join(lines[:head_lines]))
    return "\n\n".join(heads) or "No files"

# ---------- minimal health ----------

@app.get("/", response_class=PlainTextResponse)
def root():
    return "ok"

# ---------- demo repo for first-load UX ----------

_DEMO_REPO: Dict[str, str] = {
    "src/pager.py": (
        "class Pager:\n"
        "    def page(self, items, size):\n"
        "        pages = []\n"
        "        for i in range(0, len(items)):\n"
        "            if i % size == 0:\n"
        "                pages.append(items[i:i+size])\n"
        "        return pages\n"
    ),
    "README.md": "# Demo repo\n\nThis is a tiny sample used when nothing is uploaded.",
}

@app.get("/api/repo/demo")
def repo_demo() -> Dict[str, str]:
    """Return a tiny repo so the UI isn't empty on first load."""
    return _DEMO_REPO

# ---------- main endpoints used by the UI ----------

@app.post("/api/patch", response_class=PlainTextResponse)
def propose_patch(payload: Dict = Body(...)):
    """
    payload = {
      "ticket": {"key":"WB-1","title":"...","description":"..."},
      "files": {"path": "content", ...},
      "mu": 0.4
    }
    """
    ticket = payload.get("ticket") or {}
    files: Dict[str, str] = payload.get("files") or {}
    mu = float(payload.get("mu", 0.4))

    # Build style/context from uploaded or demo files
    ctx = _context_from_files(files) if files else _context_from_files(_DEMO_REPO)

    # Call your patcher/LLM
    key = ticket.get("key") or "WB-1"
    summary = ticket.get("title") or ticket.get("summary") or "Untitled"
    description = ticket.get("description") or ""
    diff = patcher.propose_patch(
        {"key": key, "summary": summary, "description": description},
        ctx,
        mu=mu,
        key=key,
    )

    return diff or "--- a/empty\n+++ b/empty\n@@\n+No patch generated\n"

@app.post("/api/patch-zip-json")
async def patch_zip_json(
    file: UploadFile = File(...),
    key: str = Form("WB-1"),
    title: str = Form("Upload"),
    description: str = Form(""),
    mu: float = Form(0.4),
):
    """
    Accept a .zip archive of a repo, extract whitelisted text files, return BOTH:
      - files: {path: text}
      - diff: LLM-proposed patch
    This powers the UI so the left file list is populated for .zip uploads.
    """
    data = await file.read()
    zf = zipfile.ZipFile(io.BytesIO(data))

    files: Dict[str, str] = {}
    for name in zf.namelist():
        if _keep(name):
            try:
                files[name] = zf.read(name).decode("utf-8", "ignore")
            except Exception:
                # skip binary or undecodable files
                pass

    ctx = _context_from_files(files) if files else _context_from_files(_DEMO_REPO)
    ticket = {"key": key, "summary": title, "description": description}
    diff = patcher.propose_patch(ticket, ctx, mu=mu, key=key) or ""

    return JSONResponse({"diff": diff, "files": files})

# (Optional) keep your older /api/patch-zip if you already use it somewhere:
@app.post("/api/patch-zip", response_class=PlainTextResponse)
async def patch_zip_legacy(
    file: UploadFile = File(...),
    key: str = Form("WB-1"),
    title: str = Form("Upload"),
    description: str = Form(""),
    mu: float = Form(0.4),
):
    data = await file.read()
    zf = zipfile.ZipFile(io.BytesIO(data))

    files: Dict[str, str] = {}
    for name in zf.namelist():
        if _keep(name):
            try:
                files[name] = zf.read(name).decode("utf-8", "ignore")
            except Exception:
                pass

    ctx = _context_from_files(files) if files else _context_from_files(_DEMO_REPO)
    ticket = {"key": key, "summary": title, "description": description}
    diff = patcher.propose_patch(ticket, ctx, mu=mu, key=key) or ""
    return diff
