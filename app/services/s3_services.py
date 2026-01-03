from app.services.s3_client import s3, S3_BUCKET_NAME

def upload_fileobj_to_s3(file_obj, s3_key: str, content_type: str):
    s3.upload_fileobj(
        Fileobj=file_obj,
        Bucket=S3_BUCKET_NAME,
        Key=s3_key,
        ExtraArgs={"ContentType": content_type}
    )
    return s3_key




def list_s3_objects(prefix: str = ""):
    response = s3.list_objects_v2(
        Bucket=S3_BUCKET_NAME,
        Prefix=prefix,
    )

    return [
        obj["Key"]
        for obj in response.get("Contents", [])
        if not obj["Key"].endswith("/")
    ]



def generate_presigned_download_url(s3_key: str, expires_in: int = 3600):
    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": S3_BUCKET_NAME,
            "Key": s3_key
        },
        ExpiresIn=expires_in
    )


def download_s3_object(s3_key: str, local_path: str):
    """
    Downloads an S3 object to a local file path.
    Used when summarizing already-uploaded videos.
    """
    try:
        s3.download_file(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Filename=local_path,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to download {s3_key} from S3") from e
