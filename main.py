from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from tiktok_client import login_and_fetch_messages
from supabase_client import store_messages, get_messages
from sessions import create_session, get_user
from models import TikTokCredentials
import uvicorn
from supabase import create_client
from typing import List
from playwright.sync_api import sync_playwright
import os
from supabase_client import supabase
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
import uuid
from supabase_client import store_session
from supabase_client import get_username_from_session
from tiktok_client import load_tiktok_state, save_tiktok_state
from fastapi.middleware.cors import CORSMiddleware



def store_messages(user_id: str, messages: list):
    for msg in messages:
        try:
            supabase.table("messages").insert({
                "user_id": user_id,
                "sender": msg['sender'],
                "content": msg['content'],
                "timestamp": msg['timestamp']
            }).execute()
        except Exception as e:
            print("❌ Fehler beim Einfügen:", e)
            print("↪ Nachricht war:", msg)



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Oder spezifische Domains wenn du später wieder sicher willst
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional: CORS-Preflight Test-Endpoint (hilft beim Debuggen)
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return JSONResponse(content={"message": "CORS preflight success"})


sessions = {}

@app.get("/check_session")
async def check_session(username: str):
    try:
        result = supabase.table("tiktok_sessions").select("username").eq("username", username).execute()
        if result.data and len(result.data) > 0:
            return {"exists": True}
        else:
            return {"exists": False}
    except Exception as e:
        print("❌ Fehler beim Session-Check:", e)
        return {"exists": False}

@app.post("/login")
async def login(request: Request):
    data = await request.json()
    username_raw = data.get("username")
    username = username_raw.strip().lower().replace(" ", "_")
    password = data.get("password")

    session_id = str(uuid.uuid4())
    store_session(session_id, username)

    already_registered = os.path.exists(f"state_{username}.json") or load_tiktok_state(username)

    return {
        "session_id": session_id,
        "registered": already_registered
    }


@app.post("/onboarding")
async def onboarding(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    # Session erstellen (wie im Login)
    session_id = str(uuid.uuid4())
    sessions[session_id] = username

    # 🚀 Direkt TikTok Login ausführen
    await login_and_fetch_messages(username, password)

    return {"message": "Onboarding erfolgreich!", "session_id": session_id}


@app.post("/fetch_messages")
async def fetch_messages(session_id: str):
    print("🧪 Session-ID erhalten:", session_id)

    user = get_username_from_session(session_id)
    print("👤 Zugeordneter Nutzer:", user)

    if not user:
        return JSONResponse(content={"error": "Ungültige Session"}, status_code=401)

    messages = await login_and_fetch_messages(user, "DEMO_PASSWORD")
    store_messages(user, messages)
    return JSONResponse(content=messages)

@app.get("/messages")
def get_saved_messages(session_id: str):
    user = get_user(session_id)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid session")
    return get_messages(user)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
