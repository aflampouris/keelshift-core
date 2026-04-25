import os
from minio import Minio


def _client() -> Minio:
    endpoint = os.environ["MINIO_ENDPOINT"].replace("http://", "").replace("https://", "")
    secure = os.environ["MINIO_ENDPOINT"].startswith("https")
    return Minio(
        endpoint=endpoint,
        access_key=os.environ["MINIO_ACCESS_KEY"],
        secret_key=os.environ["MINIO_SECRET_KEY"],
        secure=secure,
    )


def ensure_bucket(bucket: str) -> None:
    c = _client()
    if not c.bucket_exists(bucket):
        c.make_bucket(bucket)


def upload_file(bucket: str, object_key: str, file_path: str, content_type: str) -> str:
    c = _client()
    ensure_bucket(bucket)
    c.fput_object(bucket, object_key, file_path, content_type=content_type)
    return object_key

from datetime import timedelta

def get_presigned_url(object_key: str, expires: int = 3600) -> str:
    c = _client()
    bucket = os.environ.get("MINIO_BUCKET", "keelshift")

    return c.presigned_get_object(
        bucket_name=bucket,
        object_name=object_key,
        expires=timedelta(seconds=expires),  # 👈 FIX
    )