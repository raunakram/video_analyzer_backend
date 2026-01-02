from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from app.services.gemini_client import ask_gemini
from app.services.session_store import get_session
from app.services.ollama_client import ask_llm
import json
from app.utils.system_prompt import SYSTEM_PROMPT

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

    # Send first question
    first_question = QUESTIONS[0]
    session["messages"].append({"role": "assistant", "content": first_question})
    await websocket.send_json({"message": first_question})

    try:
        while True:
            user_text = await websocket.receive_text()
            session["messages"].append({"role": "user", "content": user_text})

            llm_messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                *session["messages"]
            ]

            # raw_response = ask_gemini(llm_messages)
            raw_response = ask_llm(llm_messages)
            llm_result = json.loads(raw_response)

            if llm_result["evaluation"] == "invalid":
                session["attempts"] += 1

                if session["attempts"] >= 3:
                    session["question_index"] += 1
                    session["attempts"] = 0

                    if session["question_index"] >= len(QUESTIONS):
                        await websocket.send_json({
                            "message": "Thank you. All questions are complete."
                        })
                        break

                    next_q = QUESTIONS[session["question_index"]]
                    session["messages"].append({"role": "assistant", "content": next_q})
                    await websocket.send_json({"message": next_q})
                    continue

                session["messages"].append({
                    "role": "assistant",
                    "content": llm_result["reply"]
                })
                await websocket.send_json({"message": llm_result["reply"]})
                continue

            # Valid answer → move forward
            session["question_index"] += 1
            session["attempts"] = 0

            if session["question_index"] >= len(QUESTIONS):
                await websocket.send_json({
                    "message": "Thanks! Your responses have been recorded."
                })
                break

            next_q = QUESTIONS[session["question_index"]]
            session["messages"].append({"role": "assistant", "content": next_q})
            await websocket.send_json({"message": next_q})

    except WebSocketDisconnect:
        print("Client disconnected")




@router.get("/ask")
async def ask_question():
    response = "dddddddddd"

    return {"response": response}