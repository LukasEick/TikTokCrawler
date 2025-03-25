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

