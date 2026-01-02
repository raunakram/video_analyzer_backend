from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from app.services.gemini_client import ask_gemini
from app.services.session_store import get_session
from app.services.ollama_client import ask_llm
import json
from pathlib import Path
from app.core.config import SYSTEM_PROMPT_DIR


router = APIRouter()

QUESTIONS = [
    "What was this movie trailer about?",
    "What did you like in this video?",
    "What was the most memorable scene in the video?"
]

@router.websocket("/ws/chat/{session_id}")
async def chat_ws(websocket: WebSocket, session_id: str):
    await websocket.accept()
    session = get_session(session_id)

    # Load system prompt from temp file
    prompt_path = Path(f"/tmp/{session_id}_system_prompt.txt")
    prompt_path = SYSTEM_PROMPT_DIR / f"{session_id}_system_prompt.txt"

    if not prompt_path.exists():
        await websocket.send_json({
            "message": "Session expired or invalid."
        })
        await websocket.close()
        return

    SYSTEM_PROMPT = prompt_path.read_text()

    # Send first question
    first_question = QUESTIONS[0]
    session["messages"].append({"role": "assistant", "content": first_question})
    await websocket.send_json({"message": first_question})

    try:
        while True:
            user_text = await websocket.receive_text()
            session["messages"].append({"role": "user", "content": user_text})

            # Inject system prompt ONCE
            if not session["system_added"]:
                session["messages"].insert(0, {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                })
                session["system_added"] = True

            llm_messages = session["messages"]
            raw_response = ask_llm(llm_messages)

            try:
                llm_result = json.loads(raw_response)
            except json.JSONDecodeError:
                await websocket.send_json({"message": raw_response})
                continue

            if llm_result["evaluation"] == "invalid":
                session["attempts"] += 1

                if session["attempts"] >= 3:
                    # Move forward after max attempts
                    session["question_index"] += 1
                    session["attempts"] = 0
                else:
                    # Ask guiding follow-up
                    session["messages"].append({
                        "role": "assistant",
                        "content": llm_result["reply"]
                    })
                    await websocket.send_json({"message": llm_result["reply"]})
                    continue

            elif llm_result["evaluation"] == "valid":
                session["question_index"] += 1
                session["attempts"] = 0

            elif llm_result["evaluation"] == "done":
                await websocket.send_json({
                    "message": "Thank you. All questions are complete."
                })
                break


            if session["question_index"] >= len(QUESTIONS):
                await websocket.send_json({
                    "message": "Thank you. All questions are complete."
                })
                break

            next_q = QUESTIONS[session["question_index"]]
            session["messages"].append({"role": "assistant", "content": next_q})
            await websocket.send_json({"message": next_q})

    except WebSocketDisconnect:
        pass




@router.get("/ask")
async def ask_question():
    response = "dddddddddd"

    return {"response": response}