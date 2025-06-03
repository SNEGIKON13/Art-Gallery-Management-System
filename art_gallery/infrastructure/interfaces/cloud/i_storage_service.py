"""
Interface for cloud storage services.
"""
from abc import ABC, abstractmethod
from typing import Optional, List


class IStorageService(ABC):
    """Interface for cloud storage service implementations."""

    @abstractmethod
    def ensure_bucket_exists(self, bucket_name: str) -> bool:
        """
        Ensures that the bucket exists, creates it if it doesn't.
        
        Args:
            bucket_name: Name of the bucket to check/create
            
        Returns:
            bool: True if bucket exists or was created, False otherwise
        """
        pass

    @abstractmethod
    def upload_data(self, bucket_name: str, object_name: str, data, content_type: str) -> bool:
        """
        Upload data to the storage.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object to store
            data: Data to upload (can be bytes or file-like object)
            content_type: MIME type of the data
            
        Returns:
            bool: True if upload succeeded, False otherwise
        """
        pass

    @abstractmethod
    def download_data(self, bucket_name: str, object_name: str) -> Optional[bytes]:
        """
        Download data from the storage.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object to download
            
        Returns:
            Optional[bytes]: Downloaded data or None if not found
        """
        pass

    @abstractmethod
    def delete_object(self, bucket_name: str, object_name: str) -> bool:
        """
        Delete an object from storage.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object to delete
            
        Returns:
            bool: True if delete succeeded, False otherwise
        """
        pass

    @abstractmethod
    def list_objects(self, bucket_name: str, prefix: str = "") -> List[str]:
        """
        List objects in the bucket with optional prefix.
        
        Args:
            bucket_name: Name of the bucket
            prefix: Optional prefix to filter objects
            
        Returns:
            List[str]: List of object names
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def object_exists(self, bucket_name: str, object_name: str) -> bool:
        """
        Check if an object exists.
        
        Args:
            bucket_name: Name of the bucket
            object_name: Name of the object to check
            
        Returns:
            bool: True if object exists, False otherwise
        """
        pass
