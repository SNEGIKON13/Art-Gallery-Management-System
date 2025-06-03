"""
Cloud file storage strategy implementation.
"""
import logging
from typing import Optional, Union, BinaryIO

from art_gallery.application.interfaces.cloud.i_file_storage_strategy import IFileStorageStrategy
from art_gallery.infrastructure.interfaces.cloud.i_media_service import IMediaService
from art_gallery.infrastructure.exceptions.cloud_exceptions import CloudStorageError


class CloudFileStorageStrategy(IFileStorageStrategy):
    """Implementation of file storage strategy that uses cloud storage service."""
    
    def __init__(self, media_service: IMediaService):
        """
        Initialize cloud file storage strategy.
        
        Args:
            media_service: Media service implementation for cloud storage
        """
        self.media_service = media_service
        self.logger = logging.getLogger(__name__)
    
    def upload_file(self, entity_id: int, file_data: Union[bytes, BinaryIO], filename: str) -> Optional[str]:
        """
        Upload a file to cloud storage.
        
        Args:
            entity_id: ID of the entity (artwork, exhibition, etc.)
            file_data: File contents as bytes or file-like object
            filename: Original filename
            
        Returns:
            Optional[str]: Path to the stored file or None if failed
        """
        try:
            # Convert entity_id to string for the cloud storage
            entity_id_str = str(entity_id)
            
            # Use media service to upload the file
            file_path = self.media_service.upload_artwork_image(
                artwork_id=entity_id_str,
                image_data=file_data,
                original_filename=filename
            )
            
            if file_path:
                self.logger.info(f"Successfully uploaded file for entity {entity_id} to cloud storage")
            else:
                self.logger.error(f"Failed to upload file for entity {entity_id} to cloud storage")
                
            return file_path
            
        except CloudStorageError as e:
            self.logger.error(f"Cloud storage error while uploading file for entity {entity_id}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error uploading file for entity {entity_id}: {str(e)}")
            return None
    
    def get_file_url(self, file_path: str) -> Optional[str]:
        """
        Get a URL to access the file from cloud storage.
        
        Args:
            file_path: Path to the file in cloud storage
            
        Returns:
            Optional[str]: URL to the file or None if not found
        """
        try:
            url = self.media_service.get_artwork_image_url(file_path)
            
            if url:
                self.logger.debug(f"Generated URL for file: {file_path}")
            else:
                self.logger.warning(f"Could not generate URL for file: {file_path}")
                
            return url
            
        except CloudStorageError as e:
            self.logger.error(f"Cloud storage error getting URL for file {file_path}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error getting URL for file {file_path}: {str(e)}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from cloud storage.
        
        Args:
            file_path: Path to the file in cloud storage
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            success = self.media_service.delete_artwork_image(file_path)
            
            if success:
                self.logger.info(f"Successfully deleted file: {file_path}")
            else:
                self.logger.error(f"Failed to delete file: {file_path}")
                
            return success
            
        except CloudStorageError as e:
            self.logger.error(f"Cloud storage error deleting file {file_path}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error deleting file {file_path}: {str(e)}")
            return False
