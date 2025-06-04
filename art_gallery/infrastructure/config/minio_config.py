"""
Configuration for MinIO client.
"""
import os
from dataclasses import dataclass
from typing import Optional

from .constants import (
    DEFAULT_MINIO_ENDPOINT,
    DEFAULT_MINIO_SECURE,
    DEFAULT_MINIO_BUCKET,
    DEFAULT_ARTWORK_PREFIX,
    DEFAULT_USER_PREFIX,
    DEFAULT_EXHIBITION_PREFIX
)


@dataclass
class MinioConfig:
    """Configuration for MinIO client."""
    
    # Connection settings
    endpoint: str = DEFAULT_MINIO_ENDPOINT
    access_key: str = ""
    secret_key: str = ""
    secure: bool = DEFAULT_MINIO_SECURE
    
    # Default bucket and prefix settings
    default_bucket: str = DEFAULT_MINIO_BUCKET
    artwork_prefix: str = DEFAULT_ARTWORK_PREFIX
    exhibition_prefix: str = DEFAULT_EXHIBITION_PREFIX
    user_prefix: str = DEFAULT_USER_PREFIX
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
        endpoint = os.getenv("MINIO_ENDPOINT", DEFAULT_MINIO_ENDPOINT)
        access_key = os.getenv("MINIO_ACCESS_KEY", "")
        secret_key = os.getenv("MINIO_SECRET_KEY", "")
        secure_str = os.getenv("MINIO_SECURE", str(DEFAULT_MINIO_SECURE))
        secure = secure_str.lower() in ("true", "1", "yes")
        default_bucket = os.getenv("MINIO_DEFAULT_BUCKET", DEFAULT_MINIO_BUCKET)
        
        # Optional prefixes from environment
        artwork_prefix = os.getenv("MINIO_ARTWORK_PREFIX", DEFAULT_ARTWORK_PREFIX)
        exhibition_prefix = os.getenv("MINIO_EXHIBITION_PREFIX", DEFAULT_EXHIBITION_PREFIX)
        user_prefix = os.getenv("MINIO_USER_PREFIX", DEFAULT_USER_PREFIX)
        event_prefix = os.getenv("MINIO_EVENT_PREFIX", "events/")
        
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
            default_bucket=default_bucket,
            artwork_prefix=artwork_prefix,
            exhibition_prefix=exhibition_prefix,
            user_prefix=user_prefix,
            event_prefix=event_prefix
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
