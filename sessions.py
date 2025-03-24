from uuid import uuid4

active_sessions = {}

def create_session(user: str) -> str:
    session_id = str(uuid4())
    active_sessions[session_id] = user
    return session_id

def get_user(session_id: str):
    return active_sessions.get(session_id)
