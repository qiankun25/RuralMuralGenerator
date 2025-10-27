# core/session.py
from typing import Dict
from uuid import uuid4
from models.state import MuralGenerationState

_sessions: Dict[str, MuralGenerationState] = {}

def create_session() -> str:
    session_id = str(uuid4())
    _sessions[session_id] = MuralGenerationState()
    return session_id

def get_session(session_id: str) -> MuralGenerationState:
    if session_id not in _sessions:
        raise KeyError("Session not found")
    return _sessions[session_id]

def delete_session(session_id: str):
    _sessions.pop(session_id, None)