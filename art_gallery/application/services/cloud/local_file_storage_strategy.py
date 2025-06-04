"""
Local file storage strategy implementation.
"""
import os
import uuid
import shutil
import logging
from typing import Optional, Union, BinaryIO

from art_gallery.application.interfaces.cloud.i_file_storage_strategy import IFileStorageStrategy


class LocalFileStorageStrategy(IFileStorageStrategy):
    """Implementation of file storage strategy that uses local filesystem."""
    
    def __init__(self, base_path: str):
        """
        Initialize local file storage strategy.
        
        Args:
            base_path: Base directory path for storing files
        """
        self.base_path = os.path.abspath(base_path)
        self.logger = logging.getLogger(__name__)
        
        # Create base directory if it doesn't exist
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
            self.logger.info(f"Created local storage directory at {self.base_path}")
    
    def upload_file(self, entity_id: int, file_data: Union[bytes, BinaryIO], filename: str) -> Optional[str]:
        """
        Upload a file to local storage.
        
        Args:
            entity_id: ID of the entity (artwork, exhibition, etc.)
            file_data: File contents as bytes or file-like object
            filename: Original filename
            
        Returns:
            Optional[str]: Relative path to the stored file or None if failed
        """
        try:
            # Extract file extension
            _, file_extension = os.path.splitext(filename)
            if not file_extension:
                file_extension = ".jpg"  # Default extension
            
            # Create entity directory if needed
            entity_dir = os.path.join(self.base_path, f"artwork_{entity_id}")
            if not os.path.exists(entity_dir):
                os.makedirs(entity_dir)
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            file_path = os.path.join(entity_dir, unique_filename)
            
            # Write file to disk
            if isinstance(file_data, bytes):
                with open(file_path, 'wb') as f:
                    f.write(file_data)
            else:
                # Assume file_data is a file-like object
                with open(file_path, 'wb') as f:
                    shutil.copyfileobj(file_data, f)
            
            # Return relative path (from base_path)
            rel_path = os.path.join(f"artwork_{entity_id}", unique_filename)
            rel_path = rel_path.replace('\\', '/')  # Normalize path separators
            
            self.logger.info(f"Stored file for entity {entity_id} at {rel_path}")
            return rel_path
            
        except Exception as e:
            self.logger.error(f"Failed to store file for entity {entity_id}: {str(e)}")
            return None
    
    def get_file_url(self, file_path: str) -> Optional[str]:
        """
        Get a URL or file path to access the file.
        For local storage, this returns a file:// URL.
        
        Args:
            file_path: Relative path to the file
            
        Returns:
            Optional[str]: URL to the file or None if not found
        """
        try:
            # Convert to absolute path and check if file exists
            abs_path = os.path.join(self.base_path, file_path)
            if not os.path.isfile(abs_path):
                self.logger.warning(f"File not found: {abs_path}")
                return None
                
            # Return file:// URL
            # Normalize path separators for URL format
            url_path = abs_path.replace('\\', '/')
            url = f"file:///{url_path}"
            
            return url
            
        except Exception as e:
            self.logger.error(f"Failed to get URL for file {file_path}: {str(e)}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from local storage.
        
        Args:
            file_path: Relative path to the file
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            # Convert to absolute path
            abs_path = os.path.join(self.base_path, file_path)
            
            # Check if file exists
            if not os.path.isfile(abs_path):
                self.logger.warning(f"File to delete not found: {abs_path}")
                return True  # Return True for idempotency
            
            # Delete the file
            os.remove(abs_path)
            self.logger.info(f"Deleted file: {abs_path}")
            
            # Remove empty directory if possible
            dir_path = os.path.dirname(abs_path)
            if os.path.exists(dir_path) and not os.listdir(dir_path):
                os.rmdir(dir_path)
                self.logger.info(f"Removed empty directory: {dir_path}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete file {file_path}: {str(e)}")
            return False
