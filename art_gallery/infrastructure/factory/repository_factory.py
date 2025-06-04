"""
Фабрика для создания репозиториев и UnitOfWork в зависимости от выбранного типа хранилища.
"""
from typing import Optional, Union, Literal

from art_gallery.repository.interfaces.user_repository import IUserRepository
from art_gallery.repository.interfaces.artwork_repository import IArtworkRepository
from art_gallery.repository.interfaces.exhibition_repository import IExhibitionRepository

from art_gallery.repository.implementations.file.user_repository import UserFileRepository
from art_gallery.repository.implementations.file.artwork_repository import ArtworkFileRepository
from art_gallery.repository.implementations.file.exhibition_repository import ExhibitionFileRepository
from art_gallery.repository.implementations.unit_of_work import UnitOfWork

from art_gallery.repository.implementations.minio.user_repository import UserMinioRepository
from art_gallery.repository.implementations.minio.artwork_repository import ArtworkMinioRepository
from art_gallery.repository.implementations.minio.exhibition_repository import ExhibitionMinioRepository
from art_gallery.repository.implementations.minio.unit_of_work import MinioUnitOfWork

from art_gallery.infrastructure.cloud.minio_config import MinioConfig
from art_gallery.infrastructure.cloud.minio_service import MinioService
from art_gallery.infrastructure.factory.serialization_plugin_factory import SerializationPluginFactory
from art_gallery.infrastructure.factory.minio_repository_factory import MinioRepositoryFactory

import os


class RepositoryFactory:
    """
    Фабрика для создания репозиториев и UnitOfWork в зависимости от выбранного типа хранилища.
    """
    
    # Константы для типов хранилищ
    STORAGE_FILE = "file"
    STORAGE_MINIO = "minio"
    
    @classmethod
    def create_user_repository(cls, 
                              storage_type: Literal["file", "minio"] = "file", 
                              format_name: str = "json",
                              minio_service: Optional[MinioService] = None,
                              config: Optional[MinioConfig] = None) -> IUserRepository:
        """
        Создает репозиторий пользователей указанного типа.
        
        Args:
            storage_type: Тип хранилища ("file" или "minio").
            format_name: Формат сериализации (json, xml).
            minio_service: Сервис MinIO для репозиториев MinIO.
            config: Конфигурация MinIO для репозиториев MinIO.
            
        Returns:
            IUserRepository: Репозиторий пользователей.
            
        Raises:
            ValueError: Если указан неизвестный тип хранилища.
        """
        if storage_type == cls.STORAGE_FILE:
            # Получаем сериализатор и десериализатор
            serializer = SerializationPluginFactory.get_serializer(format_name)
            deserializer = SerializationPluginFactory.get_deserializer(format_name)
            
            # Определяем путь к файлу в зависимости от формата
            filename = f"users.{format_name}"
            filepath = os.path.join("data", "file", filename)
            
            # Создаем и возвращаем файловый репозиторий
            return UserFileRepository(filepath, serializer, deserializer)
            
        elif storage_type == cls.STORAGE_MINIO:
            # Используем фабрику для MinIO репозиториев
            return MinioRepositoryFactory.create_user_repository(
                format_name=format_name,
                minio_service=minio_service,
                config=config
            )
        else:
            raise ValueError(f"Неизвестный тип хранилища: {storage_type}")
    
    @classmethod
    def create_artwork_repository(cls, 
                                 storage_type: Literal["file", "minio"] = "file", 
                                 format_name: str = "json",
                                 minio_service: Optional[MinioService] = None,
                                 config: Optional[MinioConfig] = None) -> IArtworkRepository:
        """
        Создает репозиторий экспонатов указанного типа.
        
        Args:
            storage_type: Тип хранилища ("file" или "minio").
            format_name: Формат сериализации (json, xml).
            minio_service: Сервис MinIO для репозиториев MinIO.
            config: Конфигурация MinIO для репозиториев MinIO.
            
        Returns:
            IArtworkRepository: Репозиторий экспонатов.
            
        Raises:
            ValueError: Если указан неизвестный тип хранилища.
        """
        if storage_type == cls.STORAGE_FILE:
            # Получаем сериализатор и десериализатор
            serializer = SerializationPluginFactory.get_serializer(format_name)
            deserializer = SerializationPluginFactory.get_deserializer(format_name)
            
            # Определяем путь к файлу в зависимости от формата
            filename = f"artworks.{format_name}"
            filepath = os.path.join("data", "file", filename)
            
            # Создаем и возвращаем файловый репозиторий
            return ArtworkFileRepository(filepath, serializer, deserializer)
            
        elif storage_type == cls.STORAGE_MINIO:
            # Используем фабрику для MinIO репозиториев
            return MinioRepositoryFactory.create_artwork_repository(
                format_name=format_name,
                minio_service=minio_service,
                config=config
            )
        else:
            raise ValueError(f"Неизвестный тип хранилища: {storage_type}")
    
    @classmethod
    def create_exhibition_repository(cls, 
                                    storage_type: Literal["file", "minio"] = "file", 
                                    format_name: str = "json",
                                    minio_service: Optional[MinioService] = None,
                                    config: Optional[MinioConfig] = None) -> IExhibitionRepository:
        """
        Создает репозиторий выставок указанного типа.
        
        Args:
            storage_type: Тип хранилища ("file" или "minio").
            format_name: Формат сериализации (json, xml).
            minio_service: Сервис MinIO для репозиториев MinIO.
            config: Конфигурация MinIO для репозиториев MinIO.
            
        Returns:
            IExhibitionRepository: Репозиторий выставок.
            
        Raises:
            ValueError: Если указан неизвестный тип хранилища.
        """
        if storage_type == cls.STORAGE_FILE:
            # Получаем сериализатор и десериализатор
            serializer = SerializationPluginFactory.get_serializer(format_name)
            deserializer = SerializationPluginFactory.get_deserializer(format_name)
            
            # Определяем путь к файлу в зависимости от формата
            filename = f"exhibitions.{format_name}"
            filepath = os.path.join("data", "file", filename)
            
            # Создаем и возвращаем файловый репозиторий
            return ExhibitionFileRepository(filepath, serializer, deserializer)
            
        elif storage_type == cls.STORAGE_MINIO:
            # Используем фабрику для MinIO репозиториев
            return MinioRepositoryFactory.create_exhibition_repository(
                format_name=format_name,
                minio_service=minio_service,
                config=config
            )
        else:
            raise ValueError(f"Неизвестный тип хранилища: {storage_type}")
    
    @classmethod
    def create_unit_of_work(cls, 
                           storage_type: Literal["file", "minio"] = "file", 
                           format_name: str = "json",
                           minio_service: Optional[MinioService] = None,
                           config: Optional[MinioConfig] = None) -> Union[UnitOfWork, MinioUnitOfWork]:
        """
        Создает Unit of Work для указанного типа хранилища.
        
        Args:
            storage_type: Тип хранилища ("file" или "minio").
            format_name: Формат сериализации (json, xml).
            minio_service: Сервис MinIO для репозиториев MinIO.
            config: Конфигурация MinIO для репозиториев MinIO.
            
        Returns:
            Union[UnitOfWork, MinioUnitOfWork]: Unit of Work для работы с репозиториями.
            
        Raises:
            ValueError: Если указан неизвестный тип хранилища.
        """
        if storage_type == cls.STORAGE_FILE:
            # Создаем и возвращаем стандартный UnitOfWork
            # TODO: Обновить UnitOfWork для поддержки файловых репозиториев с сериализацией
            return UnitOfWork()
            
        elif storage_type == cls.STORAGE_MINIO:
            # Используем фабрику для MinIO UnitOfWork
            return MinioRepositoryFactory.create_unit_of_work(
                format_name=format_name,
                minio_service=minio_service,
                config=config
            )
        else:
            raise ValueError(f"Неизвестный тип хранилища: {storage_type}")
