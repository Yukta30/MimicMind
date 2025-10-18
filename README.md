# MimicMind — Demo (Backend + Web)

This repo contains a FastAPI backend and a Next.js web app that demo **MimicMind**:
- Jira‑like **Workbench** to enter a ticket and propose a patch
- Unified diff output (plain text) suitable for PRs
- Slider controls "mimicness" (quirks vs best‑practice)

## Render deployment

### Backend
- Root: *(repo root)*
- Build: `pip install -r requirements.txt`
- Start: `uvicorn mimicmind.service.app:app --host 0.0.0.0 --port $PORT`

### Web
- Root: `web`
- Build: `yarn install && yarn build`
- Start: `yarn start -p $PORT`
- Env: `NEXT_PUBLIC_API_BASE = https://<YOUR-BACKEND-URL>`

## Local Dev
Backend:
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn mimicmind.service.app:app --reload --port 8080
```
Web:
```
cd web
yarn install
echo "NEXT_PUBLIC_API_BASE=http://localhost:8080" > .env.local
yarn dev
```
