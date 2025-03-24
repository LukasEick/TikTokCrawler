from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def store_messages(user_id: str, messages: list):
    for msg in messages:
        supabase.table("messages").insert({
            "user_id": user_id,
            "sender": msg['sender'],
            "content": msg['content'],
            "timestamp": msg['timestamp']
        }).execute()

def get_messages(user_id: str):
    return supabase.table("messages").select("*").eq("user_id", user_id).execute().data
