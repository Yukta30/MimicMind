from fastapi import APIRouter, Request, HTTPException
import hmac, hashlib, os
router = APIRouter()
SECRET = os.getenv("JIRA_WEBHOOK_SECRET","")
def verify(req: Request, body: bytes):
    sig = req.headers.get("X-Hub-Signature","")
    if not SECRET or not sig:
        return True
    mac = hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, mac)
@router.post("/webhooks/jira")
async def jira_webhook(req: Request):
    body = await req.body()
    if not verify(req, body):
        raise HTTPException(401, "bad signature")
    payload = await req.json()
    issue = payload.get("issue",{})
    event = payload.get("webhookEvent","unknown")
    return {"ok": True, "event": event, "key": issue.get("key")}
