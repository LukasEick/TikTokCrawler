from uuid import uuid4
from typing import Dict, Optional
import time

# In-Memory Session-Store
active_sessions: Dict[str, dict] = {}

# Optional: Session-Lifetime in Sekunden (z.B. 1 Tag)
SESSION_LIFETIME = 86400  # 24 Stunden

def create_session(user: str) -> str:
    session_id = str(uuid4())
    active_sessions[session_id] = {
        "user": user,
        "created_at": time.time()
    }
    print(f"✅ Session erstellt: {session_id} für Benutzer {user}")
    return session_id

def get_user(session_id: str) -> Optional[str]:
    session = active_sessions.get(session_id)
    if not session:
        print(f"⚠️ Keine aktive Session gefunden für ID: {session_id}")
        return None

    # Optional: Session-Timeout überprüfen
    if time.time() - session["created_at"] > SESSION_LIFETIME:
        print(f"⚠️ Session abgelaufen: {session_id}")
        active_sessions.pop(session_id, None)
        return None

    return session["user"]
