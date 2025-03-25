from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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



STATE_FILE = "state.json"



app = FastAPI()

origins = ["*"]  # Für Netlify

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login")
def login(creds: TikTokCredentials):
    session_id = create_session(creds.username)
    return {"session_id": session_id}

@app.post("/fetch_messages")
def fetch_messages(request: Request):
    data = request.query_params
    session_id = data.get("session_id")
    user = get_user(session_id)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid session")

    messages = login_and_fetch_messages(user, "DEMO_PASSWORD")  # Passwort aus Frontend oder Token
    store_messages(user, messages)
    print("📤 Sende Nachrichten an Frontend:", messages)
    return JSONResponse(content=messages)

@app.get("/messages")
def get_saved_messages(session_id: str):
    user = get_user(session_id)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid session")
    return get_messages(user)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
