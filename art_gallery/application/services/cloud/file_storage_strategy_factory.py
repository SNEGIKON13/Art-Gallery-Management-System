"""
Factory for creating file storage strategies.
"""
import logging
from typing import Optional, Dict, Any

from art_gallery.application.interfaces.cloud.i_file_storage_strategy import IFileStorageStrategy
from art_gallery.application.services.cloud.local_file_storage_strategy import LocalFileStorageStrategy
from art_gallery.application.services.cloud.cloud_file_storage_strategy import CloudFileStorageStrategy


class FileStorageStrategyFactory:
    """Factory for creating different file storage strategy implementations."""
    
    def __init__(self):
        """Initialize the factory."""
        self.logger = logging.getLogger(__name__)
    
    def create_strategy(self, strategy_type: str, **kwargs) -> Optional[IFileStorageStrategy]:
        """
        Create a file storage strategy based on the specified type.
        
        Args:
            strategy_type: Type of strategy to create ('local' or 'cloud')
            **kwargs: Additional arguments for strategy initialization
                For 'local': 
                    - base_path (str): Base directory for file storage
                For 'cloud':
                    - media_service (IMediaService): Media service for cloud storage
        
        Returns:
            Optional[IFileStorageStrategy]: The created strategy or None if invalid type
        """
        strategy_type = strategy_type.lower()
        
        if strategy_type == "local":
            return self._create_local_strategy(kwargs)
        elif strategy_type == "cloud":
            return self._create_cloud_strategy(kwargs)
        else:
            self.logger.error(f"Unknown storage strategy type: {strategy_type}")
            return None
    
    def _create_local_strategy(self, kwargs: Dict[str, Any]) -> Optional[LocalFileStorageStrategy]:
        """
        Create a local file storage strategy.
        
        Args:
            kwargs: Dictionary with strategy parameters
                - base_path (str): Base directory for file storage
        
        Returns:
            Optional[LocalFileStorageStrategy]: The created strategy or None if invalid params
        """
        base_path = kwargs.get("base_path")
        
        if not base_path:
            self.logger.error("Missing required parameter 'base_path' for local storage strategy")
            return None
            
        try:
            return LocalFileStorageStrategy(base_path=base_path)
        except Exception as e:
            self.logger.error(f"Failed to create local storage strategy: {str(e)}")
            return None
    
    def _create_cloud_strategy(self, kwargs: Dict[str, Any]) -> Optional[CloudFileStorageStrategy]:
        """
        Create a cloud file storage strategy.
        
        Args:
            kwargs: Dictionary with strategy parameters
                - media_service (IMediaService): Media service for cloud storage
        
        Returns:
            Optional[CloudFileStorageStrategy]: The created strategy or None if invalid params
        """
        media_service = kwargs.get("media_service")
        
        if not media_service:
            self.logger.error("Missing required parameter 'media_service' for cloud storage strategy")
            return None
            
        try:
            return CloudFileStorageStrategy(media_service=media_service)
        except Exception as e:
            self.logger.error(f"Failed to create cloud storage strategy: {str(e)}")
            return None
