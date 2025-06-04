"""
Interface for media file operations.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, BinaryIO, Union


class IMediaService(ABC):
    """Interface for services that handle media file operations."""
    
    @abstractmethod
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
        pass

    @abstractmethod
    def get_artwork_image(self, image_path: str) -> Optional[bytes]:
        """
        Get an artwork image by its path.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Optional[bytes]: Image data or None if not found
        """
        pass

    @abstractmethod
    def delete_artwork_image(self, image_path: str) -> bool:
        """
        Delete an artwork image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            bool: True if deleted successfully
        """
        pass

    @abstractmethod
    def get_artwork_image_url(self, image_path: str, expires: int = 3600) -> Optional[str]:
        """
        Get a URL to access an artwork image.
        
        Args:
            image_path: Path to the image
            expires: URL expiration time in seconds
            
        Returns:
            Optional[str]: URL to the image or None if not found
        """
        pass

    @abstractmethod
    def list_artwork_images(self, artwork_id: str) -> List[str]:
        """
        List all images for a specific artwork.
        
        Args:
            artwork_id: ID of the artwork
            
        Returns:
            List[str]: List of image paths
        """
        pass
