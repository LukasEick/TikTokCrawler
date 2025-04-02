import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

def get_messages(user_id: str):
    try:
        result = supabase.table("messages").select("*").eq("user_id", user_id).execute()
        return result.data
    except Exception as e:
        print("❌ Fehler beim Abrufen:", e)
        return []

def store_session(session_id: str, username: str):
    try:
        supabase.table("sessions").upsert({
            "session_id": session_id,
            "username": username
        }).execute()
    except Exception as e:
        print("❌ Fehler beim Speichern der Session:", e)


def get_username_from_session(session_id: str) -> str | None:
    try:
        result = supabase.table("sessions").select("username").eq("session_id", session_id).execute()
        data = result.data
        if data and len(data) > 0:
            return data[0]["username"]
    except Exception as e:
        print("❌ Fehler beim Abrufen der Session:", e)
    return None


def save_tiktok_state(username: str, state_file_path: str):
    try:
        with open(state_file_path, "r") as f:
            state_data = json.load(f)
        supabase.table("tiktok_sessions").upsert({
            "username": username,
            "state_json": state_data
        }).execute()
    except Exception as e:
        print("❌ Fehler beim Speichern der TikTok-Session:", e)


def load_tiktok_state(username: str) -> bool:
    try:
        result = supabase.table("tiktok_sessions").select("state_json").eq("username", username).execute()
        data = result.data
        if data and len(data) > 0:
            with open(f"state_{username}.json", "w") as f:
                json.dump(data[0]["state_json"], f)
            return True
    except Exception as e:
        print("❌ Fehler beim Laden der TikTok-Session:", e)
    return False

