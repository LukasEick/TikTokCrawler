from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tiktok_client import login_and_fetch_messages
from supabase_client import store_messages, get_messages, supabase, store_session, get_username_from_session
from sessions import create_session, get_user
import os
import uuid
import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor

# ThreadPool erstellen
executor = ThreadPoolExecutor(max_workers=2)

# Windows Fix
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://serene-biscuit-c4a067.netlify.app",
        "https://precious-rolypoly-9d9b00.netlify.app",
        "https://00c1-2a01-4f8-c17-eb2e-00-1.ngrok-free.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Preflight für CORS
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return JSONResponse(content={"message": "CORS preflight success"})

# Sessions Dictionary
sessions = {}

# Session Check
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

# Login Endpoint
@app.post("/login")
async def login(request: Request):
    data = await request.json()
    username_raw = data.get("username")
    username = username_raw.strip().lower().replace(" ", "_")

    session_id = str(uuid.uuid4())
    store_session(session_id, username)

    already_registered = os.path.exists(f"state_{username}.json")

    return {
        "session_id": session_id,
        "registered": already_registered
    }

# Onboarding Endpoint (Session erzeugen & speichern)
@app.post("/onboarding")
async def onboarding(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    session_id = str(uuid.uuid4())
    sessions[session_id] = username

    # ✅ WICHTIG: Sync-Funktion im Executor ausführen
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, login_and_fetch_messages, username, password)

    return {"message": "Onboarding erfolgreich!", "session_id": session_id}

# Server-Status
@app.get("/")
def read_root():
    return {"status": "✅ Server läuft!"}

# Nachrichten holen (Achtung: Sync!)
@app.post("/fetch_messages")
async def fetch_messages(session_id: str):
    print("🧪 Session-ID erhalten:", session_id)

    user = get_username_from_session(session_id)
    print("👤 Zugeordneter Nutzer:", user)

    if not user:
        return JSONResponse(content={"error": "Ungültige Session"}, status_code=401)

    # ✅ Nachrichten sync abrufen!
    loop = asyncio.get_event_loop()
    messages = await loop.run_in_executor(executor, login_and_fetch_messages, user, "DEMO_PASSWORD")

    store_messages(user, messages)

    return JSONResponse(content=messages)

# Gespeicherte Nachrichten aus Supabase abrufen
@app.get("/messages")
def get_saved_messages(session_id: str):
    user = get_user(session_id)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid session")

    return get_messages(user)

# Server starten
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
