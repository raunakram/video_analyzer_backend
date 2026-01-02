sessions = {}

def get_session(session_id):
    if session_id not in sessions:
        sessions[session_id] = {
            "messages": [],
            "question_index": 0,
            "attempts": 0
        }
    return sessions[session_id]
