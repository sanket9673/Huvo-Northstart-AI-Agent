from typing import List, Dict, Any, Optional

class SessionData:
    """Holds the conversation history and configuration flags for a session."""
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.opt_out: bool = False

class MemoryService:
    """Singleton service to manage in-memory session states."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MemoryService, cls).__new__(cls, *args, **kwargs)
            cls._instance.sessions = {}
        return cls._instance

    def get_or_create_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Returns conversation message history list for the session, creating it if needed."""
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionData()
        return self.sessions[session_id].history

    def add_message(self, session_id: str, role: str, content: Optional[str], **kwargs) -> None:
        """Appends a message to history, supporting additional fields like tool_calls/tool_call_id."""
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionData()
        
        msg = {"role": role, "content": content}
        for k, v in kwargs.items():
            if v is not None:
                msg[k] = v
        self.sessions[session_id].history.append(msg)

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Returns formatted messages."""
        if session_id not in self.sessions:
            return []
        return self.sessions[session_id].history

    def clear_session(self, session_id: str) -> None:
        """Clears conversation history for the session."""
        if session_id in self.sessions:
            self.sessions[session_id].history.clear()

    def mark_opt_out(self, session_id: str) -> None:
        """Flags session as opted out / DND."""
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionData()
        self.sessions[session_id].opt_out = True

    def is_opted_out(self, session_id: str) -> bool:
        """Returns opt-out status."""
        if session_id not in self.sessions:
            return False
        return self.sessions[session_id].opt_out
