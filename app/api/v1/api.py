from fastapi import APIRouter

from .endpoints import upload, chat, voice_assistant, s3_routes

api_router = APIRouter()

api_router.include_router(upload.router, prefix="/v1", tags=["Uploads"])
api_router.include_router(chat.router, prefix="/v1", tags=["Chat"])
api_router.include_router(s3_routes.router, prefix="/v1", tags=["S3"])
# api_router.include_router(voice_assistant.router, prefix="/v1", tags=["Voice assistant"])
