"""
Фабрика для создания MinIO репозиториев и сервисов.
"""
from typing import Optional

from art_gallery.repository.interfaces.user_repository import IUserRepository
from art_gallery.repository.interfaces.artwork_repository import IArtworkRepository
from art_gallery.repository.interfaces.exhibition_repository import IExhibitionRepository
from art_gallery.repository.implementations.minio.user_repository import UserMinioRepository
from art_gallery.repository.implementations.minio.artwork_repository import ArtworkMinioRepository
from art_gallery.repository.implementations.minio.exhibition_repository import ExhibitionMinioRepository
from art_gallery.repository.implementations.minio.unit_of_work import MinioUnitOfWork

from art_gallery.application.interfaces.cloud.i_media_service import IMediaService
from art_gallery.infrastructure.cloud.minio_service import MinioService
from art_gallery.infrastructure.cloud.minio_config import MinioConfig
from art_gallery.infrastructure.cloud.media_service import MediaService
from art_gallery.infrastructure.factory.serialization_plugin_factory import SerializationPluginFactory


class MinioRepositoryFactory:
    """
    Фабрика для создания репозиториев и сервисов, использующих MinIO.
    """

    @classmethod
    def create_minio_service(cls, config: Optional[MinioConfig] = None) -> MinioService:
        """
        Создает сервис для работы с MinIO.
        
        Args:
            config: Конфигурация MinIO. Если не указана, используется конфигурация по умолчанию.
            
        Returns:
            MinioService: Сервис для работы с MinIO.
        """
        minio_config = config or MinioConfig.from_env()
        return MinioService(minio_config)

    @classmethod
    def create_media_service(cls, 
                           minio_service: Optional[MinioService] = None, 
                           config: Optional[MinioConfig] = None) -> MediaService:
        """
        Создает сервис для работы с медиа-файлами.
        
        Args:
            minio_service: Сервис MinIO. Если не указан, создается новый.
            config: Конфигурация MinIO. Если не указана, используется конфигурация по умолчанию.
            
        Returns:
            MediaService: Сервис для работы с медиа-файлами.
        """
        minio_config = config or MinioConfig.from_env()
        service = minio_service or cls.create_minio_service(minio_config)
        return MediaService(service, minio_config)

    @classmethod
    def create_user_repository(cls, 
                             format_name: str = "json", 
                             minio_service: Optional[MinioService] = None, 
                             config: Optional[MinioConfig] = None) -> IUserRepository:
        """
        Создает репозиторий пользователей, использующий MinIO.
        
        Args:
            format_name: Формат сериализации (json, xml).
            minio_service: Сервис MinIO. Если не указан, создается новый.
            config: Конфигурация MinIO. Если не указана, используется конфигурация по умолчанию.
            
        Returns:
            IUserRepository: Репозиторий пользователей.
        """
        minio_config = config or MinioConfig.from_env()
        service = minio_service or cls.create_minio_service(minio_config)
        
        serializer = SerializationPluginFactory.get_serializer(format_name)
        deserializer = SerializationPluginFactory.get_deserializer(format_name)
        
        return UserMinioRepository(
            serializer=serializer,
            deserializer=deserializer,
            minio_service=service,
            config=minio_config
        )

    @classmethod
    def create_artwork_repository(cls, 
                                format_name: str = "json", 
                                minio_service: Optional[MinioService] = None, 
                                config: Optional[MinioConfig] = None) -> IArtworkRepository:
        """
        Создает репозиторий экспонатов, использующий MinIO.
        
        Args:
            format_name: Формат сериализации (json, xml).
            minio_service: Сервис MinIO. Если не указан, создается новый.
            config: Конфигурация MinIO. Если не указана, используется конфигурация по умолчанию.
            
        Returns:
            IArtworkRepository: Репозиторий экспонатов.
        """
        minio_config = config or MinioConfig.from_env()
        service = minio_service or cls.create_minio_service(minio_config)
        
        serializer = SerializationPluginFactory.get_serializer(format_name)
        deserializer = SerializationPluginFactory.get_deserializer(format_name)
        
        return ArtworkMinioRepository(
            serializer=serializer,
            deserializer=deserializer,
            minio_service=service,
            config=minio_config
        )

    @classmethod
    def create_exhibition_repository(cls, 
                                   format_name: str = "json", 
                                   minio_service: Optional[MinioService] = None, 
                                   config: Optional[MinioConfig] = None) -> IExhibitionRepository:
        """
        Создает репозиторий выставок, использующий MinIO.
        
        Args:
            format_name: Формат сериализации (json, xml).
            minio_service: Сервис MinIO. Если не указан, создается новый.
            config: Конфигурация MinIO. Если не указана, используется конфигурация по умолчанию.
            
        Returns:
            IExhibitionRepository: Репозиторий выставок.
        """
        minio_config = config or MinioConfig.from_env()
        service = minio_service or cls.create_minio_service(minio_config)
        
        serializer = SerializationPluginFactory.get_serializer(format_name)
        deserializer = SerializationPluginFactory.get_deserializer(format_name)
        
        return ExhibitionMinioRepository(
            serializer=serializer,
            deserializer=deserializer,
            minio_service=service,
            config=minio_config
        )

    @classmethod
    def create_unit_of_work(cls, 
                          format_name: str = "json", 
                          minio_service: Optional[MinioService] = None, 
                          config: Optional[MinioConfig] = None) -> MinioUnitOfWork:
        """
        Создает Unit of Work для работы с MinIO репозиториями.
        
        Args:
            format_name: Формат сериализации (json, xml).
            minio_service: Сервис MinIO. Если не указан, создается новый.
            config: Конфигурация MinIO. Если не указана, используется конфигурация по умолчанию.
            
        Returns:
            MinioUnitOfWork: Unit of Work для работы с MinIO репозиториями.
        """
        minio_config = config or MinioConfig.from_env()
        service = minio_service or cls.create_minio_service(minio_config)
        
        return MinioUnitOfWork(
            format_name=format_name,
            minio_service=service,
            config=minio_config
        )
