import os
import io
import uuid
import logging
import base64
from typing import Dict, Any, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings

logger = logging.getLogger(__name__)

class EncryptedObjectStorageService:
    """
    Enterprise Encrypted Object Storage Service.
    Applies client-side AES-256 (Fernet) payload encryption before persisting files
    to AWS S3 / S3-compatible Object Storage with Server-Side Encryption (SSE-KMS/AES-256).
    Falls back to local encrypted disk storage when S3 credentials are not supplied.
    """

    def __init__(self):
        # Derives a deterministic Fernet key from STORAGE_ENCRYPTION_KEY
        key_raw = settings.STORAGE_ENCRYPTION_KEY.encode('utf-8')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"ContractLens_Storage_Salt_2026",
            iterations=100000,
        )
        fernet_key = base64.urlsafe_b64encode(kdf.derive(key_raw))
        self.cipher = Fernet(fernet_key)

        # Check if AWS S3 Object Storage is configured
        self.use_s3 = bool(settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY and settings.S3_BUCKET_NAME)
        
        if self.use_s3:
            import boto3
            session_kwargs = {
                "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
                "region_name": settings.AWS_REGION_NAME
            }
            if settings.S3_ENDPOINT_URL:
                session_kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL
                
            self.s3_client = boto3.client("s3", **session_kwargs)
            self.bucket_name = settings.S3_BUCKET_NAME
            logger.info(f"Initialized AWS S3 Encrypted Object Storage for bucket: {self.bucket_name}")
        else:
            self.s3_client = None
            self.local_storage_dir = os.path.abspath("./encrypted_storage")
            os.makedirs(self.local_storage_dir, exist_ok=True)
            logger.info(f"Initialized Local AES-256 Encrypted Storage at: {self.local_storage_dir}")

    def encrypt_bytes(self, content: bytes) -> bytes:
        """Encrypts raw byte content using AES-256 Fernet cipher."""
        return self.cipher.encrypt(content)

    def decrypt_bytes(self, encrypted_content: bytes) -> bytes:
        """Decrypts AES-256 Fernet encrypted byte content."""
        return self.cipher.decrypt(encrypted_content)

    def upload_file(self, filename: str, file_bytes: bytes) -> Dict[str, Any]:
        """
        Encrypts and stores a file in Object Storage or Encrypted Local Storage.
        Returns metadata including storage provider, file_key, and encryption status.
        """
        encrypted_bytes = self.encrypt_bytes(file_bytes)
        unique_id = str(uuid.uuid4())
        safe_filename = filename.replace(" ", "_")
        file_key = f"contracts/{unique_id}_{safe_filename}.enc"

        if self.use_s3 and self.s3_client:
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=file_key,
                    Body=encrypted_bytes,
                    ServerSideEncryption="AES256",
                    ContentType="application/octet-stream",
                    Metadata={
                        "original_filename": filename,
                        "encryption": "AES256-Fernet"
                    }
                )
                logger.info(f"Successfully uploaded encrypted document to S3: {file_key}")
                return {
                    "storage_type": "AWS_S3",
                    "bucket": self.bucket_name,
                    "file_key": file_key,
                    "original_name": filename,
                    "encrypted": True,
                    "size_bytes": len(file_bytes),
                    "encrypted_size_bytes": len(encrypted_bytes)
                }
            except Exception as e:
                logger.error(f"S3 Upload failed, falling back to local encrypted store: {e}")

        # Local Encrypted Storage Fallback
        local_path = os.path.join(self.local_storage_dir, f"{unique_id}_{safe_filename}.enc")
        with open(local_path, "wb") as f:
            f.write(encrypted_bytes)

        logger.info(f"Successfully stored encrypted file locally at: {local_path}")
        return {
            "storage_type": "LOCAL_ENCRYPTED_AES256",
            "file_key": local_path,
            "original_name": filename,
            "encrypted": True,
            "size_bytes": len(file_bytes),
            "encrypted_size_bytes": len(encrypted_bytes)
        }

    def fetch_file(self, file_key: str) -> bytes:
        """
        Retrieves and decrypts a file from S3 or Local Encrypted Storage.
        """
        if self.use_s3 and self.s3_client and not os.path.exists(file_key):
            try:
                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
                encrypted_bytes = response["Body"].read()
                return self.decrypt_bytes(encrypted_bytes)
            except Exception as e:
                logger.error(f"Failed to fetch file from S3: {e}")
                raise ValueError(f"File key {file_key} could not be retrieved from S3.")

        if os.path.exists(file_key):
            with open(file_key, "rb") as f:
                encrypted_bytes = f.read()
            return self.decrypt_bytes(encrypted_bytes)

        raise FileNotFoundError(f"Encrypted document at {file_key} does not exist.")

storage_service = EncryptedObjectStorageService()
