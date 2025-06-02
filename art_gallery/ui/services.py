from dataclasses import dataclass
from art_gallery.application.services.mocks.mock_user_service import MockUserService
from art_gallery.application.services.mocks.mock_artwork_service import MockArtworkService
from art_gallery.application.services.mocks.mock_exhibition_service import MockExhibitionService
from art_gallery.application.interfaces.user_service import IUserService
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.application.interfaces.exhibition_service import IExhibitionService
from art_gallery.infrastructure.config.cli_config import CLIConfig
from art_gallery.infrastructure.factory.serialization_plugin_factory import SerializationPluginFactory
import os

# Реальные сервисы
from art_gallery.application.services.user_service import UserService
from art_gallery.application.services.artwork_service import ArtworkService
from art_gallery.application.services.exhibition_service import ExhibitionService

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
    serialization_factory: SerializationPluginFactory

def create_mock_services() -> ServiceCollection:
    # Инициализируем фабрику плагинов сериализации
    factory = SerializationPluginFactory()
    factory.initialize()
    
    return ServiceCollection(
        user_service=MockUserService(),
        artwork_service=MockArtworkService(),
        exhibition_service=MockExhibitionService(),
        cli_config=CLIConfig(),
        serialization_factory=factory
    )

def create_real_services(format_name: str = 'json'):
    """Создает экземпляры реальных сервисов с рабочими репозиториями
    
    Args:
        format_name (str, optional): Формат данных для хранения ('json' или 'xml'). По умолчанию 'json'.
    
    Returns:
        Tuple[UserService, ArtworkService, ExhibitionService]: 
            Возвращает три сервиса: пользователей, произведений искусства и выставок
    """
    # Пути к файлам данных с учетом выбранного формата
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Проверяем и нормализуем формат
    if format_name.lower() not in ['json', 'xml']:
        print(f"Предупреждение: Неподдерживаемый формат '{format_name}'. Используем JSON по умолчанию.")
        format_name = 'json'
    
    file_ext = format_name.lower()
    users_file = os.path.join(data_dir, f'users.{file_ext}')
    artworks_file = os.path.join(data_dir, f'artworks.{file_ext}')
    exhibitions_file = os.path.join(data_dir, f'exhibitions.{file_ext}')
    
    print(f"Используем формат данных: {format_name.upper()}")
    
    # Инициализация фабрики плагинов сериализации
    factory = SerializationPluginFactory()
    factory.initialize()  # Загрузка всех плагинов
    
    # Получаем сериализатор и десериализатор выбранного формата
    serializer = factory.get_serializer(format_name)
    deserializer = factory.get_deserializer(format_name)
    
    # Инициализация реальных репозиториев
    # Передаем сериализаторы и десериализаторы в репозитории
    user_repo = UserFileRepository(users_file, serializer, deserializer)
    artwork_repo = ArtworkFileRepository(artworks_file, serializer, deserializer)
    exhibition_repo = ExhibitionFileRepository(exhibitions_file, serializer, deserializer)

    # Инициализация реальных сервисов
    user_service = UserService(user_repo)
    artwork_service = ArtworkService(artwork_repo) # ArtworkService ожидает IBaseRepository[Artwork]
    exhibition_service = ExhibitionService(exhibition_repo, artwork_repo) # ExhibitionService требует IExhibitionRepository и IArtworkRepository

    # Создаем CLIConfig
    cli_config = CLIConfig()
    
    return ServiceCollection(
        user_service=user_service,
        artwork_service=artwork_service,
        exhibition_service=exhibition_service,
        cli_config=cli_config,
        serialization_factory=factory
    )
