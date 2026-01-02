from fastapi import APIRouter

from .endpoints import items, upload, chat

api_router = APIRouter()

api_router.include_router(upload.router, prefix="/v1", tags=["Uploads"])
api_router.include_router(items.router, prefix="/v1/items", tags=["items"])
api_router.include_router(chat.router, prefix="/v1", tags=["Chat"])
