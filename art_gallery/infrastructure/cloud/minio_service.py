"""
MinioService implementation for cloud storage.
"""
import io
import logging
from datetime import timedelta
from typing import List, Optional, Union, BinaryIO

from minio import Minio
from minio.error import S3Error

from art_gallery.infrastructure.interfaces.cloud.i_storage_service import IStorageService
from art_gallery.infrastructure.config.minio_config import MinioConfig
from art_gallery.exceptions.cloud_exceptions import (
    BucketCreationError, 
    ObjectUploadError, 
    ObjectDownloadError,
    ObjectDeleteError, 
    ObjectNotFoundError, 
    BucketNotFoundError,
    AuthenticationError, 
    ConnectionError
)


class MinioService(IStorageService):
    """MinIO implementation of storage service interface."""

    def __init__(self, config: MinioConfig):
        """
        Initialize MinIO client with provided configuration.
        
        Args:
            config: MinioConfig instance with connection details
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        try:
            self.client = Minio(
                endpoint=config.endpoint,
                access_key=config.access_key,
                secret_key=config.secret_key,
                secure=config.secure
            )
            self.logger.info(f"MinIO client initialized with endpoint {config.endpoint}")
        except Exception as e:
            self.logger.error(f"Failed to initialize MinIO client: {str(e)}")
            raise ConnectionError(f"Could not connect to MinIO server: {str(e)}")

    def ensure_bucket_exists(self, bucket_name: str) -> bool:
        """
        Ensures that the bucket exists, creates it if it doesn't.
        
        Args:
            bucket_name: Name of the bucket to check/create
            
        Returns:
            bool: True if bucket exists or was created
            
        Raises:
            BucketCreationError: If bucket creation fails
        """
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                self.logger.info(f"Created bucket '{bucket_name}'")
            return True
        except S3Error as e:
            self.logger.error(f"Failed to ensure bucket exists: {str(e)}")
            raise BucketCreationError(f"Failed to create bucket '{bucket_name}': {str(e)}")

    def upload_data(self, bucket_name: str, object_name: str, data: Union[bytes, BinaryIO], content_type: str) -> bool:
        """
        Upload data to the storage.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object to store
            data: Data to upload (can be bytes or file-like object)
            content_type: MIME type of the data
            
        Returns:
            bool: True if upload succeeded
            
        Raises:
            ObjectUploadError: If upload fails
            BucketNotFoundError: If bucket doesn't exist
        """
        try:
            # Ensure the bucket exists
            if not self.client.bucket_exists(bucket_name):
                raise BucketNotFoundError(f"Bucket '{bucket_name}' not found")
            
            # Convert bytes to file-like object if needed
            if isinstance(data, bytes):
                data = io.BytesIO(data)
                
            # Get the length of the data
            data.seek(0, io.SEEK_END)
            length = data.tell()
            data.seek(0)
            
            # Upload the object
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=data,
                length=length,
                content_type=content_type
            )
            self.logger.info(f"Uploaded object '{object_name}' to bucket '{bucket_name}'")
            return True
        except S3Error as e:
            self.logger.error(f"Failed to upload object '{object_name}': {str(e)}")
            raise ObjectUploadError(f"Failed to upload '{object_name}': {str(e)}")

    def download_data(self, bucket_name: str, object_name: str) -> Optional[bytes]:
        """
        Download data from the storage.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object to download
            
        Returns:
            Optional[bytes]: Downloaded data or None if not found
            
        Raises:
            ObjectDownloadError: If download fails
            ObjectNotFoundError: If object doesn't exist
        """
        try:
            # Check if object exists
            if not self.object_exists(bucket_name, object_name):
                raise ObjectNotFoundError(f"Object '{object_name}' not found in bucket '{bucket_name}'")
                
            # Get the object
            response = self.client.get_object(bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            
            self.logger.info(f"Downloaded object '{object_name}' from bucket '{bucket_name}'")
            return data
        except S3Error as e:
            self.logger.error(f"Failed to download object '{object_name}': {str(e)}")
            raise ObjectDownloadError(f"Failed to download '{object_name}': {str(e)}")

    def delete_object(self, bucket_name: str, object_name: str) -> bool:
        """
        Delete an object from storage.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object to delete
            
        Returns:
            bool: True if delete succeeded
            
        Raises:
            ObjectDeleteError: If delete fails
            ObjectNotFoundError: If object doesn't exist
        """
        try:
            # Check if object exists
            if not self.object_exists(bucket_name, object_name):
                raise ObjectNotFoundError(f"Object '{object_name}' not found in bucket '{bucket_name}'")
                
            # Remove the object
            self.client.remove_object(bucket_name, object_name)
            self.logger.info(f"Deleted object '{object_name}' from bucket '{bucket_name}'")
            return True
        except S3Error as e:
            self.logger.error(f"Failed to delete object '{object_name}': {str(e)}")
            raise ObjectDeleteError(f"Failed to delete '{object_name}': {str(e)}")

    def list_objects(self, bucket_name: str, prefix: str = "") -> List[str]:
        """
        List objects in the bucket with optional prefix.
        
        Args:
            bucket_name: Name of the bucket
            prefix: Optional prefix to filter objects
            
        Returns:
            List[str]: List of object names
        """
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix, recursive=True)
            object_names = [obj.object_name for obj in objects]
            return object_names
        except S3Error as e:
            self.logger.error(f"Failed to list objects with prefix '{prefix}': {str(e)}")
            return []

    def get_object_url(self, bucket_name: str, object_name: str, expires: int = 3600) -> Optional[str]:
        """
        Get a presigned URL for the object.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object
            expires: Expiry time in seconds
            
        Returns:
            Optional[str]: Presigned URL or None if object doesn't exist
        """
        try:
            if not self.object_exists(bucket_name, object_name):
                return None
                
            # Convert seconds to timedelta as required by the minio library
            expires_delta = timedelta(seconds=expires)
            url = self.client.presigned_get_object(bucket_name, object_name, expires=expires_delta)
            return url
        except S3Error as e:
            self.logger.error(f"Failed to get URL for object '{object_name}': {str(e)}")
            return None

    def object_exists(self, bucket_name: str, object_name: str) -> bool:
        """
        Check if an object exists.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object to check
            
        Returns:
            bool: True if object exists, False otherwise
        """
        try:
            self.client.stat_object(bucket_name, object_name)
            return True
        except S3Error as e:
            # S3 returns a 404 if the object doesn't exist, which raises an S3Error
            # We should check the error code to make sure it's actually a "not found" error
            if hasattr(e, "code") and e.code == "NoSuchKey":
                return False
            self.logger.error(f"Error checking if object '{object_name}' exists: {str(e)}")
            return False
