import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import List, Optional

# 🔑 .env laden
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Supabase URL oder API Key fehlt in .env Datei!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ Nachrichten speichern
def store_messages(user_id: str, messages: List[dict]):
    if not messages:
        print("ℹ️ Keine Nachrichten zum Speichern vorhanden.")
        return

    for msg in messages:
        try:
            supabase.table("messages").insert({
                "user_id": user_id,
                "sender": msg.get('sender', ''),
                "content": msg.get('content', ''),
                "timestamp": msg.get('timestamp', '')
            }).execute()
            print(f"✅ Nachricht gespeichert für {user_id}")
        except Exception as e:
            print("❌ Fehler beim Einfügen:", e)
            print("↪ Nachricht war:", msg)

# ✅ Nachrichten abrufen
def get_messages(user_id: str) -> List[dict]:
    try:
        result = supabase.table("messages").select("*").eq("user_id", user_id).execute()
        return result.data or []
    except Exception as e:
        print("❌ Fehler beim Abrufen:", e)
        return []

# ✅ Session speichern
def store_session(session_id: str, username: str):
    try:
        supabase.table("sessions").upsert({
            "session_id": session_id,
            "username": username
        }).execute()
        print(f"✅ Session gespeichert: {session_id} -> {username}")
    except Exception as e:
        print("❌ Fehler beim Speichern der Session:", e)

# ✅ Session abrufen
def get_username_from_session(session_id: str) -> Optional[str]:
    try:
        result = supabase.table("sessions").select("username").eq("session_id", session_id).execute()
        data = result.data
        if data and len(data) > 0:
            return data[0].get("username")
    except Exception as e:
        print("❌ Fehler beim Abrufen der Session:", e)
    return None

# ✅ TikTok-Session speichern
def save_tiktok_state(username: str, state_file_path: str):
    if not os.path.exists(state_file_path):
        print(f"❌ State-Datei {state_file_path} existiert nicht!")
        return

    try:
        with open(state_file_path, "r") as f:
            state_data = json.load(f)

        if not state_data:
            print("⚠️ State-Datei ist leer oder ungültig!")
            return

        supabase.table("tiktok_sessions").upsert({
            "username": username,
            "state_json": state_data
        }).execute()
        print(f"✅ TikTok-Session gespeichert für Benutzer: {username}")

    except Exception as e:
        print("❌ Fehler beim Speichern der TikTok-Session:", e)

# ✅ TikTok-Session laden
def load_tiktok_state(username: str) -> bool:
    try:
        result = supabase.table("tiktok_sessions").select("state_json").eq("username", username).execute()
        data = result.data
        if data and len(data) > 0 and data[0].get("state_json"):
            with open(f"state_{username}.json", "w") as f:
                json.dump(data[0]["state_json"], f)
            print(f"✅ State für {username} geladen!")
            return True
        else:
            print(f"⚠️ Keine gespeicherte State für {username} gefunden.")
    except Exception as e:
        print("❌ Fehler beim Laden der TikTok-Session:", e)
    return False
