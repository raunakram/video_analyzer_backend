SESSIONS = {}

def get_session(session_id: str):
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "messages": [],
            "question_index": 0,
            "attempts": 0,
            "system_added": False
        }
    return SESSIONS[session_id]
