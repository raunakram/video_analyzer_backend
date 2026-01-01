from fastapi import APIRouter

from .endpoints import items, upload

api_router = APIRouter()

api_router.include_router(upload.router, prefix="/v1", tags=["Uploads"])
api_router.include_router(items.router, prefix="/v1/items", tags=["items"])
