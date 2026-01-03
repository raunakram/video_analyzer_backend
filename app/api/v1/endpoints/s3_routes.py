from fastapi import APIRouter, UploadFile, File, Query
from app.services.s3_services import (
    upload_fileobj_to_s3,
    list_s3_objects,
    generate_presigned_download_url
)

router = APIRouter()



@router.post("/upload-to-s3")
async def upload_to_s3(file: UploadFile = File(...)):
    s3_key = f"videos/{file.filename}"

    upload_fileobj_to_s3(
        file_obj=file.file,
        s3_key=s3_key,
        content_type=file.content_type
    )

    download_url = generate_presigned_download_url(s3_key)

    return {
        "message": "File uploaded successfully",
        "s3_key": s3_key,
        "download_url": download_url
    }




@router.get("/list-all-s3-objects")
async def list_bucket_objects(prefix: str = Query(default="videos/")):
    objects = list_s3_objects(prefix)

    result = []
    for obj in objects:
        result.append({
            "s3_key": obj,
            "download_url": generate_presigned_download_url(obj)
        })

    return {
        "count": len(result),
        "objects": result
    }




@router.get("/download-url")
async def get_download_url(s3_key: str):
    url = generate_presigned_download_url(s3_key)
    return {
        "s3_key": s3_key,
        "download_url": url
    }


