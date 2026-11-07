import os
import boto3
from botocore.exceptions import ClientError


def get_s3_client():
    """Initializes and returns an S3 client instance."""
    return boto3.client("s3")


def upload_image(bucket_name: str, file_path: str, object_name: str = None) -> bool:
    """
    Uploads an image file to an AWS S3 bucket.

    :param bucket_name: Target S3 bucket name
    :param file_path: Path to the local file to upload
    :param object_name: S3 object name (key). If not specified, file_path basename is used.
    :return: True if upload succeeded, False otherwise
    """
    if object_name is None:
        object_name = os.path.basename(file_path)

    s3_client = get_s3_client()
    try:
        # Determine content type based on file extension
        content_type = (
            "image/jpeg" if file_path.endswith((".jpg", ".jpeg")) else "image/png"
        )

        s3_client.upload_file(
            Filename=file_path,
            Bucket=bucket_name,
            Key=object_name,
            ExtraArgs={"ContentType": content_type},
        )
        print(f"[SUCCESS] Uploaded '{file_path}' to '{bucket_name}/{object_name}'")
        return True
    except ClientError as e:
        print(f"[ERROR] Failed to upload image: {e}")
        return False


def download_image(bucket_name: str, object_name: str, output_path: str) -> bool:
    """
    Downloads an image file from an AWS S3 bucket.

    :param bucket_name: Source S3 bucket name
    :param object_name: S3 object key to download
    :param output_path: Path where the file should be saved locally
    :return: True if download succeeded, False otherwise
    """
    s3_client = get_s3_client()
    try:
        s3_client.download_file(
            Bucket=bucket_name, Key=object_name, Filename=output_path
        )
        print(f"[SUCCESS] Downloaded '{object_name}' to '{output_path}'")
        return True
    except ClientError as e:
        print(f"[ERROR] Failed to download image: {e}")
        return False


def generate_presigned_url(
    bucket_name: str, object_name: str, expiration: int = 3600
) -> str:
    """
    Generates a presigned URL to temporarily grant access to download an S3 object.

    :param bucket_name: S3 bucket name
    :param object_name: S3 object key
    :param expiration: Expiration time in seconds (default: 1 hour)
    :return: Temporary HTTP URL string
    """
    s3_client = get_s3_client()
    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
        return url
    except ClientError as e:
        print(f"[ERROR] Failed to generate presigned URL: {e}")
        return ""


if __name__ == "__main__":
    BUCKET = "my-sample-bucket-name"
    LOCAL_IMAGE = "sample.jpg"
    REMOTE_KEY = "uploads/sample.jpg"
    DOWNLOADED_IMAGE = "downloaded_sample.jpg"

    # 1. Upload image
    upload_image(bucket_name=BUCKET, file_path=LOCAL_IMAGE, object_name=REMOTE_KEY)

    # 2. Generate temporary GET presigned URL
    temp_url = generate_presigned_url(bucket_name=BUCKET, object_name=REMOTE_KEY)
    print(f"[INFO] Presigned URL: {temp_url}")

    # 3. Download image
    download_image(
        bucket_name=BUCKET, object_name=REMOTE_KEY, output_path=DOWNLOADED_IMAGE
    )
