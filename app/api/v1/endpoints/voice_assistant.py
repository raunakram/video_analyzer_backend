# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# from app.services.ollama_client import ask_llm
# from app.services.session_store import get_session
# # from app.utils.system_prompt import SYSTEM_PROMPT
# import json
# import logging
# import traceback

# logger = logging.getLogger(__name__)
# router = APIRouter()

# QUESTIONS = [
#     "What was this movie trailer about?",
#     "What did you like in this video?",
#     "What was the most memorable scene in the video?"
# ]


# def initialize_session(session):
#     """Initialize or reset session with all required keys."""
#     if "messages" not in session:
#         session["messages"] = []
#     if "attempts" not in session:
#         session["attempts"] = 0
#     if "question_index" not in session:
#         session["question_index"] = 0
#     if "system_added" not in session:
#         session["system_added"] = False
#     if "completed" not in session:
#         session["completed"] = False
    
#     logger.info(f"Session initialized: attempts={session['attempts']}, "
#                 f"question_index={session['question_index']}, "
#                 f"completed={session['completed']}")


# @router.websocket("/ws/voice-chat/{session_id}")
# async def voice_chat_ws(websocket: WebSocket, session_id: str):
#     await websocket.accept()
#     logger.info(f"WebSocket connected for session: {session_id}")
    
#     try:
#         session = get_session(session_id)
#         logger.info(f"Session retrieved: {session_id}")
#     except Exception as e:
#         logger.error(f"Failed to get session {session_id}: {e}")
#         await websocket.send_json({
#             "type": "error",
#             "message": f"Failed to initialize session: {str(e)}"
#         })
#         await websocket.close()
#         return

#     # Initialize session with all required keys
#     initialize_session(session)

#     try:
#         # If this is a new or reset session, send first question
#         if not session.get("completed", False) and session.get("question_index", 0) < len(QUESTIONS):
#             current_index = session.get("question_index", 0)
            
#             # Only send question if we haven't sent one yet or if we're at the beginning
#             if current_index == 0 and len(session.get("messages", [])) == 0:
#                 first_question = QUESTIONS[0]
#                 session["messages"].append({"role": "assistant", "content": first_question})
                
#                 await websocket.send_json({
#                     "type": "question",
#                     "message": first_question
#                 })
#                 logger.info(f"Sent first question: {first_question}")
#             elif current_index > 0 and current_index < len(QUESTIONS):
#                 # Resume with current question
#                 current_question = QUESTIONS[current_index]
#                 await websocket.send_json({
#                     "type": "question",
#                     "message": current_question
#                 })
#                 logger.info(f"Resuming with question {current_index + 1}: {current_question}")

#         while True:
#             # Receive message from client
#             data = await websocket.receive()
            
#             # Handle both text and binary messages
#             if "text" in data:
#                 user_text = data["text"].strip()
#                 logger.info(f"Received text message: {user_text[:50]}...")
#             elif "bytes" in data:
#                 try:
#                     json_data = json.loads(data["bytes"].decode())
#                     user_text = json_data.get("message", "").strip()
#                     logger.info(f"Received JSON message: {user_text[:50]}...")
#                 except:
#                     user_text = ""
#             else:
#                 continue
            
#             if not user_text:
#                 await websocket.send_json({
#                     "type": "error",
#                     "message": "Empty message received"
#                 })
#                 continue
            
#             # Store user message
#             if "messages" not in session:
#                 session["messages"] = []
#             session["messages"].append({
#                 "role": "user",
#                 "content": user_text
#             })

#             # Inject system prompt if not already added
#             if not session.get("system_added", False):
#                 try:
#                     if SYSTEM_PROMPT:
#                         session["messages"].insert(0, {
#                             "role": "system",
#                             "content": SYSTEM_PROMPT
#                         })
#                         session["system_added"] = True
#                         logger.info("System prompt added to messages")
#                 except Exception as e:
#                     logger.error(f"Failed to add system prompt: {e}")

#             # Call LLM
#             try:
#                 logger.info(f"Calling LLM with {len(session['messages'])} messages")
                
#                 # Check if we have messages to send
#                 if not session.get("messages"):
#                     raise ValueError("No messages in session")
                
#                 raw_response = ask_llm(session["messages"])
#                 logger.info(f"LLM raw response (first 200 chars): {raw_response[:200]}...")
                
#                 if not raw_response:
#                     raise ValueError("LLM returned empty response")
                
#                 # Try to parse as JSON, fallback to plain text
#                 try:
#                     llm_result = json.loads(raw_response)
#                     logger.info(f"LLM parsed as JSON: evaluation={llm_result.get('evaluation')}")
#                 except json.JSONDecodeError:
#                     logger.warning(f"LLM response is not JSON: {raw_response[:100]}...")
#                     # Fallback: treat as plain text response
#                     await websocket.send_json({
#                         "type": "response",
#                         "message": raw_response
#                     })
#                     continue
                
#                 # Handle invalid answer
#                 evaluation = llm_result.get("evaluation", "").lower()
#                 if evaluation == "invalid":
#                     session["attempts"] = session.get("attempts", 0) + 1
#                     logger.info(f"Invalid answer, attempt {session['attempts']}/3")
                    
#                     if session["attempts"] >= 3:
#                         # Move to next question after 3 failed attempts
#                         session["question_index"] = session.get("question_index", 0) + 1
#                         session["attempts"] = 0
#                         logger.info(f"Moving to next question. Index: {session['question_index']}")
                        
#                         if session["question_index"] >= len(QUESTIONS):
#                             session["completed"] = True
#                             await websocket.send_json({
#                                 "type": "complete",
#                                 "message": "Thank you. All questions are complete."
#                             })
#                             logger.info("All questions completed")
#                             break
                        
#                         next_q = QUESTIONS[session["question_index"]]
#                         session["messages"].append({
#                             "role": "assistant",
#                             "content": next_q
#                         })
                        
#                         await websocket.send_json({
#                             "type": "question",
#                             "message": next_q
#                         })
#                         logger.info(f"Sent next question: {next_q}")
#                         continue
                    
#                     # Send invalid response message
#                     await websocket.send_json({
#                         "type": "response",
#                         "message": llm_result.get("reply", "I didn't understand that. Could you try again?")
#                     })
#                     continue
                
#                 # Valid answer - move to next question
#                 session["question_index"] = session.get("question_index", 0) + 1
#                 session["attempts"] = 0
#                 logger.info(f"Valid answer, moving to question {session['question_index']}")
                
#                 if session["question_index"] >= len(QUESTIONS):
#                     session["completed"] = True
#                     await websocket.send_json({
#                         "type": "complete",
#                         "message": "Thanks! Your responses have been recorded."
#                     })
#                     logger.info("Interview completed successfully")
#                     break
                
#                 # Send next question
#                 next_q = QUESTIONS[session["question_index"]]
#                 session["messages"].append({
#                     "role": "assistant",
#                     "content": next_q
#                 })
                
#                 await websocket.send_json({
#                     "type": "question",
#                     "message": next_q
#                 })
#                 logger.info(f"Sent next question: {next_q}")
                
#             except Exception as e:
#                 logger.error(f"Error processing message: {e}")
#                 logger.error(traceback.format_exc())
#                 await websocket.send_json({
#                     "type": "error",
#                     "message": f"Sorry, I encountered an error while processing your message: {str(e)}"
#                 })
                
#     except WebSocketDisconnect:
#         logger.info(f"Client disconnected from session: {session_id}")
#     except Exception as e:
#         logger.error(f"WebSocket error: {e}")
#         logger.error(traceback.format_exc())
#         try:
#             await websocket.send_json({
#                 "type": "error",
#                 "message": f"Connection error: {str(e)}"
#             })
#         except:
#             pass