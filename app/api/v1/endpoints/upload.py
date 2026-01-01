from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from google.genai import Client
from google.genai.types import UploadFileConfig
import os
import tempfile
import time

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyB_hVgO9DWogYHzOa7czzwM_n9p_7VqyWo"
MODEL_NAME = "gemini-2.5-flash"

client = Client(api_key=GEMINI_API_KEY)

video_memory = {}


@router.post("/upload-video/")
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


@router.post("/ask/")
async def ask_question(video_id: str = Form(...), question: str = Form(...)):
    if video_id not in video_memory:
        return JSONResponse({"error": "Upload video first"}, status_code=400)

    context = video_memory[video_id]["summary"]

    prompt = f"""
    You are answering based only on the video context below.
    Video Context:
    {context}

    Question: {question}
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return {"response": response.text}