from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from google.genai import Client
from google.genai.types import UploadFileConfig
import time
from app.services.open_router import summarize_video_with_openrouter
import tempfile
import os
from app.utils.system_prompt import SYSTEM_PROMPT_TEMPLATE
import uuid
from pathlib import Path
from app.core.config import SYSTEM_PROMPT_DIR




router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyB_hVgO9DWogYHzOa7czzwM_n9p_7VqyWo"
MODEL_NAME = "gemini-2.5-flash"

client = Client(api_key=GEMINI_API_KEY)

video_memory = {}


@router.post("/upload-video/gemini-model")
async def upload_video(video: UploadFile = File(...)):
    try:
        # Read video bytes
        video_bytes = await video.read()
        
        # Create a temporary file to save the video
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video.filename)[1]) as tmp_file:
            tmp_file.write(video_bytes)
            tmp_file_path = tmp_file.name
        
        try:
            # Upload the file to Gemini with config
            with open(tmp_file_path, 'rb') as f:
                uploaded_file = client.files.upload(
                    file=f,
                    config=UploadFileConfig(
                        mime_type=video.content_type,
                        display_name=video.filename
                    )
                )
            
            # Wait for the file to be processed (especially important for videos)
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(2)
                uploaded_file = client.files.get(name=uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                raise ValueError("Video processing failed")
            
            # Generate content with the uploaded video
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[
                    uploaded_file,
                    "Analyze this video and provide detailed scene understanding, people, actions, events, objects, environment and timeline."
                ]
            )
            
            summary = response.text
            video_id = video.filename
            
            # Store both summary and file reference
            video_memory[video_id] = {
                "summary": summary,
                "file": uploaded_file
            }
            
            return {"video_id": video_id, "summary": summary}
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)





@router.post("/summarize-video/open-router")
async def summarize_video(video: UploadFile = File(...)):
    # Save file temporarily (only for metadata / preprocessing)
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await video.read())
        video_path = tmp.name

    try:
        context = f"""
                This is a short video clip.

                Important instructions:
                - Keep descriptions generalized and non-specific
                - If details are unclear, describe them abstractly

                Task:
                Provide a structured video summary with:
                1. A brief overview of what the video appears to be about
                2. Name of characters and scene-by-scene breakdown (with timestamps)
                3. Key themes or emotions conveyed
                4. The most memorable aspect (in abstract terms)
                5. An overall impression of the video
                6. Look for key figures and what they were doing

                The video filename is: "{video.filename}"
            """


        summary = summarize_video_with_openrouter(context)


        session_id = str(uuid.uuid4())
        prompt_text = SYSTEM_PROMPT_TEMPLATE.format(summary=summary)

        # prompt_file = Path(f"/tmp/{session_id}_system_prompt.txt")
        prompt_path = SYSTEM_PROMPT_DIR / f"{session_id}_system_prompt.txt"
        prompt_path.write_text(prompt_text)

        # prompt_file.write_text(prompt_text)

        return {
            "session_id": session_id,
            "video_id": video.filename,
            "summary": summary
        }

    finally:
        os.unlink(video_path)
