import os
import logging
from dataclasses import dataclass
from typing import Optional

from art_gallery.infrastructure.config.config_registry import ConfigRegistry

# Сервисы и интерфейсы приложения
from art_gallery.application.services.mocks.mock_user_service import MockUserService
from art_gallery.application.services.mocks.mock_artwork_service import MockArtworkService
from art_gallery.application.services.mocks.mock_exhibition_service import MockExhibitionService
from art_gallery.application.interfaces.user_service import IUserService
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.application.interfaces.exhibition_service import IExhibitionService

# Облачное хранение
from art_gallery.application.interfaces.cloud.i_file_storage_strategy import IFileStorageStrategy
from art_gallery.application.interfaces.cloud.i_media_service import IMediaService
from art_gallery.application.services.cloud.local_file_storage_strategy import LocalFileStorageStrategy
from art_gallery.application.services.cloud.cloud_file_storage_strategy import CloudFileStorageStrategy
from art_gallery.infrastructure.cloud.minio_service import MinioService
from art_gallery.infrastructure.config.minio_config import MinioConfig
from art_gallery.infrastructure.interfaces.cloud.i_storage_service import IStorageService

# Конфигурация
from art_gallery.infrastructure.config.cli_config import CLIConfig
from art_gallery.infrastructure.config.storage_config import StorageConfig
from art_gallery.infrastructure.factory.serialization_plugin_factory import SerializationPluginFactory

# Реальные сервисы
from art_gallery.application.services.file.user_service import UserService
from art_gallery.application.services.file.artwork_service import ArtworkService
from art_gallery.application.services.file.exhibition_service import ExhibitionService

# Реальные репозитории
from art_gallery.repository.implementations.file.user_repository import UserFileRepository
from art_gallery.repository.implementations.file.artwork_repository import ArtworkFileRepository
from art_gallery.repository.implementations.file.exhibition_repository import ExhibitionFileRepository

# Интерфейсы репозиториев (если нужны для типизации, но сервисы ожидают конкретные реализации или интерфейсы)
from art_gallery.repository.interfaces.user_repository import IUserRepository
from art_gallery.repository.interfaces.artwork_repository import IArtworkRepository # Используется ExhibitionService
from art_gallery.repository.interfaces.exhibition_repository import IExhibitionRepository
from art_gallery.repository.interfaces.base_repository import IBaseRepository # Для ArtworkService

@dataclass
class ServiceCollection:
    user_service: IUserService
    artwork_service: IArtworkService
    exhibition_service: IExhibitionService
    cli_config: CLIConfig
    storage_config: StorageConfig
    serialization_factory: SerializationPluginFactory
    storage_service: Optional[IStorageService] = None
    media_service: Optional[IMediaService] = None
    file_storage_strategy: Optional[IFileStorageStrategy] = None

def create_mock_services() -> ServiceCollection:
    """Создает и настраивает тестовые сервисы с тестовыми хранилищами"""
    # Инициализируем фабрику плагинов сериализации
    factory = SerializationPluginFactory()
    factory.initialize()
    
    # Создаем конфигурацию CLI и хранилища
    cli_config = CLIConfig()
    storage_config = StorageConfig(storage_type='local')
    
    # Создаем стратегию хранения файлов для мок-сервисов
    storage_service = None
    media_service = None
    file_storage = None
    
    try:
        # Для тестового режима всегда используем локальную стратегию
        file_storage = LocalFileStorageStrategy(storage_config.local_storage_path)
        logging.info("Mock services using local file storage strategy")
    except Exception as e:
        logging.warning(f"Failed to create file storage strategy for mock services: {str(e)}")
    
    # Создаем мок-сервисы со стратегией хранения файлов
    artwork_service = MockArtworkService(file_storage_strategy=file_storage)
    
    return ServiceCollection(
        user_service=MockUserService(),
        artwork_service=artwork_service,
        exhibition_service=MockExhibitionService(),
        cli_config=cli_config,
        storage_config=storage_config,
        serialization_factory=factory,
        storage_service=storage_service,
        media_service=media_service,
        file_storage_strategy=file_storage
    )

def create_real_services(format_name: str = 'json'):
    """Создает экземпляры реальных сервисов с рабочими репозиториями и стратегиями хранения
    
    Args:
        format_name (str, optional): Формат данных для хранения ('json' или 'xml'). По умолчанию 'json'.
    
    Returns:
        ServiceCollection: Коллекция всех сервисов для работы приложения
    """
    # Определяем директорию с данными
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Проверяем и нормализуем формат
    if format_name.lower() not in ['json', 'xml']:
        print(f"Предупреждение: Неподдерживаемый формат '{format_name}'. Используем JSON по умолчанию.")
        format_name = 'json'
    
    # Создаем подпапку для формата
    format_dir = os.path.join(data_dir, format_name.lower())
    os.makedirs(format_dir, exist_ok=True)
    
    # Создаем пути к файлам в соответствующей подпапке
    users_file = os.path.join(format_dir, 'users.{}'.format(format_name.lower()))
    artworks_file = os.path.join(format_dir, 'artworks.{}'.format(format_name.lower()))
    exhibitions_file = os.path.join(format_dir, 'exhibitions.{}'.format(format_name.lower()))
    
    
    # Инициализация фабрики плагинов сериализации
    factory = SerializationPluginFactory()
    factory.initialize(verbose=False)  # Загрузка всех плагинов без подробного вывода
    
    # Получаем сериализатор и десериализатор выбранного формата
    serializer = factory.get_serializer(format_name)
    deserializer = factory.get_deserializer(format_name)
    
    # Инициализация реальных репозиториев
    # Передаем сериализаторы и десериализаторы в репозитории
    user_repo = UserFileRepository(users_file, serializer, deserializer)
    artwork_repo = ArtworkFileRepository(artworks_file, serializer, deserializer)
    exhibition_repo = ExhibitionFileRepository(exhibitions_file, serializer, deserializer)

    # Получаем конфигурации из централизованного реестра
    config_registry = ConfigRegistry()
    
    # Если реестр не прошел валидацию в run.py, то мы сюда не дойдем,
    # но на всякий случай проверим
    if not config_registry.is_valid():
        logging.error("Configuration registry is not valid. Using default configurations.")
        # Создадим резервные конфигурации
        cli_config = CLIConfig()
        storage_config = StorageConfig.from_env()
        minio_config = None
    else:
        # Получаем проверенные конфигурации
        cli_config = config_registry.get_cli_config()
        storage_config = config_registry.get_storage_config()
        minio_config = config_registry.get_minio_config()
        
        # Логируем информацию о конфигурации
        logging.debug(f"Storage config: type={storage_config.storage_type}, path={storage_config.local_storage_path}")
        if minio_config:
            logging.debug(f"MinIO config: endpoint={minio_config.endpoint}, bucket={minio_config.default_bucket}")
    
    # Инициализируем сервисы для хранения файлов
    storage_service = None
    media_service = None
    file_storage: Optional[IFileStorageStrategy] = None
    
    try:
        # Настраиваем стратегию хранения файлов в соответствии с конфигурацией
        if storage_config.storage_type.lower() == "cloud" and minio_config:
            try:
                logging.debug("Initializing MinIO services from registry configuration...")
                storage_service = MinioService(minio_config)
                logging.debug("MinioService initialized successfully.")
                
                # Создаем стратегию облачного хранения с правильным бакетом
                logging.debug("Creating CloudFileStorageStrategy with bucket: " + minio_config.default_bucket)
                file_storage = CloudFileStorageStrategy(storage_service, minio_config.default_bucket)
                
                # Установим media_service в None, так как мы не используем этот интерфейс
                media_service = None
                logging.info("Successfully initialized cloud (MinIO) file storage strategy.")
            except Exception as cloud_error:
                logging.warning(f"Failed to initialize cloud storage: {str(cloud_error)}", exc_info=True)
                # Если произошла ошибка, используем локальную стратегию как запасной вариант
                file_storage = LocalFileStorageStrategy(storage_config.local_storage_path)
                logging.info("Using local file storage as fallback after cloud init failure")
        else:
            logging.info("Using local file storage strategy (from configuration or as fallback)")
            file_storage = LocalFileStorageStrategy(storage_config.local_storage_path)
            logging.info("Initialized local file storage strategy")
    except Exception as e:
        logging.warning(f"Failed to initialize file storage strategy: {str(e)}", exc_info=True)
        # Если произошла ошибка, используем локальную стратегию как резервную
        try:
            # Создаем локальное хранилище как резервное
            file_storage = LocalFileStorageStrategy(storage_config.local_storage_path)
            logging.info("Using local file storage as fallback")
        except Exception as fallback_error:
            logging.error(f"Fallback storage initialization failed: {str(fallback_error)}")
            file_storage = None
    
    # Инициализация реальных сервисов
    user_service = UserService(user_repo)
    artwork_service = ArtworkService(artwork_repo, file_storage_strategy=file_storage)
    exhibition_service = ExhibitionService(exhibition_repo, artwork_repo)
    
    return ServiceCollection(
        user_service=user_service,
        artwork_service=artwork_service,
        exhibition_service=exhibition_service,
        cli_config=cli_config,
        storage_config=storage_config,
        serialization_factory=factory,
        storage_service=storage_service,
        media_service=media_service,
        file_storage_strategy=file_storage
    )
