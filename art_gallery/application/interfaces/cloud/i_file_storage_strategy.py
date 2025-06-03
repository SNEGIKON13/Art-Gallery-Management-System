"""
Interface for file storage strategies.
"""
from abc import ABC, abstractmethod
from typing import Optional, Union, BinaryIO


class IFileStorageStrategy(ABC):
    """
    Interface for file storage strategies.
    Defines methods for storing and retrieving files using different storage backends.
    """
    
    @abstractmethod
    def upload_file(self, entity_id: int, file_data: Union[bytes, BinaryIO], filename: str) -> Optional[str]:
        """
        Upload a file associated with an entity.
        
        Args:
            entity_id: ID of the entity the file belongs to
            file_data: File contents as bytes or file-like object
            filename: Original filename to preserve extension
            
        Returns:
            Optional[str]: Path or identifier of the stored file, or None if upload failed
        """
        pass
        
    @abstractmethod
    def get_file_url(self, file_path: str) -> Optional[str]:
        """
        Get a URL to access the file.
        
        Args:
            file_path: Path or identifier of the file
            
        Returns:
            Optional[str]: URL to access the file, or None if file not found
        """
        pass
        
    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: Path or identifier of the file
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        pass
