"""
MediaService implementation for handling media files.
"""
import os
import uuid
import logging
import mimetypes
from typing import Optional, List, BinaryIO, Union

from art_gallery.infrastructure.interfaces.cloud.i_storage_service import IStorageService
from art_gallery.infrastructure.interfaces.cloud.i_media_service import IMediaService
from art_gallery.infrastructure.config.minio_config import MinioConfig
from art_gallery.exceptions.cloud_exceptions import (
    ObjectUploadError, 
    ObjectDownloadError,
    ObjectDeleteError, 
    ObjectNotFoundError
)


class MediaService(IMediaService):
    """Service for handling media files storage and retrieval."""

    def __init__(self, storage_service: IStorageService, config: MinioConfig):
        """
        Initialize the media service.
        
        Args:
            storage_service: Storage service implementation
            config: MinIO configuration
        """
        self.storage_service = storage_service
        self.config = config
        self.bucket_name = config.default_bucket
        self.logger = logging.getLogger(__name__)
        
        # Ensure the default bucket exists
        self.storage_service.ensure_bucket_exists(self.bucket_name)

    def upload_artwork_image(self, artwork_id: str, image_data: Union[bytes, BinaryIO], 
                            original_filename: str) -> Optional[str]:
        """
        Upload an image for an artwork.
        
        Args:
            artwork_id: ID of the artwork
            image_data: Image data as bytes or file-like object
            original_filename: Original filename to preserve file extension
            
        Returns:
            Optional[str]: Path to stored image or None if upload failed
        """
        try:
            # Generate a unique filename while preserving the extension
            _, file_extension = os.path.splitext(original_filename)
            if not file_extension:
                file_extension = ".jpg"  # Default extension if none provided
            
            # Generate a unique file name with the original extension
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            
            # Construct the full object path
            object_path = f"{self.config.artwork_prefix}{artwork_id}/{unique_filename}"
            
            # Determine content type
            content_type = mimetypes.guess_type(original_filename)[0]
            if not content_type:
                content_type = "image/jpeg"  # Default content type
            
            # Upload the file
            success = self.storage_service.upload_data(
                self.bucket_name, 
                object_path, 
                image_data, 
                content_type
            )
            
            if success:
                self.logger.info(f"Uploaded image for artwork {artwork_id}: {object_path}")
                return object_path
            else:
                self.logger.error(f"Failed to upload image for artwork {artwork_id}")
                return None
                
        except ObjectUploadError as e:
            self.logger.error(f"Error uploading artwork image: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error uploading artwork image: {str(e)}")
            return None

    def get_artwork_image(self, image_path: str) -> Optional[bytes]:
        """
        Get an artwork image by its path.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Optional[bytes]: Image data or None if not found
        """
        try:
            data = self.storage_service.download_data(self.bucket_name, image_path)
            return data
        except ObjectDownloadError as e:
            self.logger.error(f"Error downloading artwork image: {str(e)}")
            return None
        except ObjectNotFoundError:
            self.logger.warning(f"Image not found: {image_path}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error getting artwork image: {str(e)}")
            return None

    def delete_artwork_image(self, image_path: str) -> bool:
        """
        Delete an artwork image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            success = self.storage_service.delete_object(self.bucket_name, image_path)
            if success:
                self.logger.info(f"Deleted artwork image: {image_path}")
            return success
        except ObjectDeleteError as e:
            self.logger.error(f"Error deleting artwork image: {str(e)}")
            return False
        except ObjectNotFoundError:
            # Consider it a success if the object doesn't exist
            self.logger.warning(f"Image to delete not found: {image_path}")
            return True
        except Exception as e:
            self.logger.error(f"Unexpected error deleting artwork image: {str(e)}")
            return False

    def get_artwork_image_url(self, image_path: str, expires: int = 3600) -> Optional[str]:
        """
        Get a URL to access an artwork image.
        
        Args:
            image_path: Path to the image
            expires: URL expiration time in seconds
            
        Returns:
            Optional[str]: URL to the image or None if not found
        """
        try:
            url = self.storage_service.get_object_url(self.bucket_name, image_path, expires)
            return url
        except Exception as e:
            self.logger.error(f"Error getting URL for artwork image: {str(e)}")
            return None

    def list_artwork_images(self, artwork_id: str) -> List[str]:
        """
        List all images for a specific artwork.
        
        Args:
            artwork_id: ID of the artwork
            
        Returns:
            List[str]: List of image paths
        """
        try:
            prefix = f"{self.config.artwork_prefix}{artwork_id}/"
            object_paths = self.storage_service.list_objects(self.bucket_name, prefix)
            return object_paths
        except Exception as e:
            self.logger.error(f"Error listing artwork images: {str(e)}")
            return []
            
    def extract_entity_id_from_path(self, image_path: str) -> Optional[str]:
        """
        Extract the entity ID from an image path.
        
        Args:
            image_path: Path of the image
            
        Returns:
            Optional[str]: Entity ID or None if path format is invalid
        """
        try:
            # Path format: {prefix}{entity_id}/{filename}
            # Example: artworks/123/abc123.jpg
            parts = image_path.split('/')
            if len(parts) >= 2:
                return parts[-2]  # The ID is the second-to-last part
            return None
        except Exception:
            return None
