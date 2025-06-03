"""
Configuration for MinIO client.
"""
import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class MinioConfig:
    """Configuration for MinIO client."""
    
    # Connection settings
    endpoint: str
    access_key: str
    secret_key: str
    secure: bool
    
    # Default bucket and prefix settings
    default_bucket: str
    artwork_prefix: str = "artworks/"
    exhibition_prefix: str = "exhibitions/"
    user_prefix: str = "users/"
    event_prefix: str = "events/"
    
    @classmethod
    def from_env(cls) -> 'MinioConfig':
        """
        Create a MinioConfig instance from environment variables.
        
        The following environment variables are used:
        - MINIO_ENDPOINT: MinIO server endpoint (e.g. "minio.example.com:9000")
        - MINIO_ACCESS_KEY: MinIO access key
        - MINIO_SECRET_KEY: MinIO secret key
        - MINIO_USE_SSL: Whether to use SSL (True/False)
        - MINIO_DEFAULT_BUCKET: Default bucket name for gallery media
        
        Returns:
            MinioConfig: Configuration instance
        """
        load_dotenv()
        
        endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        access_key = os.getenv("MINIO_ACCESS_KEY", "")
        secret_key = os.getenv("MINIO_SECRET_KEY", "")
        secure = os.getenv("MINIO_USE_SSL", "False").lower() in ("true", "1", "yes")
        default_bucket = os.getenv("MINIO_DEFAULT_BUCKET", "gallery-media")
        
        # Validate required settings
        if not access_key or not secret_key:
            raise ValueError(
                "MinIO credentials not found in environment variables. "
                "Please set MINIO_ACCESS_KEY and MINIO_SECRET_KEY."
            )
        
        return cls(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
            default_bucket=default_bucket
        )
    
    def get_prefix_for_entity_type(self, entity_type: str) -> str:
        """
        Get the appropriate prefix for an entity type.
        
        Args:
            entity_type: Type of entity ('artwork', 'exhibition', 'user', 'event')
            
        Returns:
            str: The prefix for the entity type
        """
        entity_type = entity_type.lower()
        if entity_type == 'artwork':
            return self.artwork_prefix
        elif entity_type == 'exhibition':
            return self.exhibition_prefix
        elif entity_type == 'user':
            return self.user_prefix
        elif entity_type == 'event':
            return self.event_prefix
        else:
            return f"{entity_type}/"
