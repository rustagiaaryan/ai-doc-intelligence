# FILE: services/document-service/app/s3_client.py

import aioboto3
from botocore.exceptions import ClientError
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class S3Client:
    """Async S3 client for file operations."""

    def __init__(self):
        self.session = aioboto3.Session(
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION,
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        self.endpoint_url = settings.S3_ENDPOINT_URL
        self.use_ssl = settings.USE_SSL

    async def ensure_bucket_exists(self):
        """Create bucket if it doesn't exist."""
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint_url,
            use_ssl=self.use_ssl
        ) as s3:
            try:
                await s3.head_bucket(Bucket=self.bucket_name)
                logger.info(f"Bucket {self.bucket_name} already exists")
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    await s3.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Created bucket {self.bucket_name}")
                else:
                    raise

    async def upload_file(self, file_data: bytes, s3_key: str, content_type: Optional[str] = None) -> bool:
        """
        Upload file to S3.

        Args:
            file_data: File contents as bytes
            s3_key: S3 object key
            content_type: MIME type of the file

        Returns:
            True if successful, False otherwise
        """
        try:
            async with self.session.client(
                's3',
                endpoint_url=self.endpoint_url,
                use_ssl=self.use_ssl
            ) as s3:
                extra_args = {}
                if content_type:
                    extra_args['ContentType'] = content_type

                await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=file_data,
                    **extra_args
                )
                logger.info(f"Uploaded file to s3://{self.bucket_name}/{s3_key}")
                return True
        except Exception as e:
            logger.error(f"Error uploading file to S3: {e}")
            return False

    async def download_file(self, s3_key: str) -> Optional[bytes]:
        """
        Download file from S3.

        Args:
            s3_key: S3 object key

        Returns:
            File contents as bytes, or None if error
        """
        try:
            async with self.session.client(
                's3',
                endpoint_url=self.endpoint_url,
                use_ssl=self.use_ssl
            ) as s3:
                response = await s3.get_object(Bucket=self.bucket_name, Key=s3_key)
                async with response['Body'] as stream:
                    return await stream.read()
        except Exception as e:
            logger.error(f"Error downloading file from S3: {e}")
            return None

    async def delete_file(self, s3_key: str) -> bool:
        """
        Delete file from S3.

        Args:
            s3_key: S3 object key

        Returns:
            True if successful, False otherwise
        """
        try:
            async with self.session.client(
                's3',
                endpoint_url=self.endpoint_url,
                use_ssl=self.use_ssl
            ) as s3:
                await s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
                logger.info(f"Deleted file s3://{self.bucket_name}/{s3_key}")
                return True
        except Exception as e:
            logger.error(f"Error deleting file from S3: {e}")
            return False

    async def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for temporary file access.

        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds

        Returns:
            Presigned URL or None if error
        """
        try:
            async with self.session.client(
                's3',
                endpoint_url=self.endpoint_url,
                use_ssl=self.use_ssl
            ) as s3:
                url = await s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': s3_key},
                    ExpiresIn=expiration
                )
                return url
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None


# Singleton instance
s3_client = S3Client()
