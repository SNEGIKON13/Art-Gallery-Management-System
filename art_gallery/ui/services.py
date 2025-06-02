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

# Предполагаемые реальные репозитории (пути могут потребовать корректировки)
from art_gallery.repository.implementations.json.user_json_repository import UserJsonRepository
from art_gallery.repository.implementations.json.artwork_json_repository import ArtworkJsonRepository
from art_gallery.repository.implementations.json.exhibition_json_repository import ExhibitionJsonRepository

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

def create_real_services() -> ServiceCollection:
    # Пути к файлам данных (можно будет вынести в конфигурацию позже)
    data_dir = "data" 
    users_file = os.path.join(data_dir, "users.json")
    artworks_file = os.path.join(data_dir, "artworks.json")
    exhibitions_file = os.path.join(data_dir, "exhibitions.json")

    # Убедимся, что директория data существует
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Инициализация реальных репозиториев
    # Убедитесь, что конструкторы репозиториев соответствуют (например, принимают filepath)
    user_repo = UserJsonRepository(users_file)
    artwork_repo = ArtworkJsonRepository(artworks_file)
    exhibition_repo = ExhibitionJsonRepository(exhibitions_file)

    # Инициализация реальных сервисов
    user_service = UserService(user_repo)
    artwork_service = ArtworkService(artwork_repo) # ArtworkService ожидает IBaseRepository[Artwork]
    exhibition_service = ExhibitionService(exhibition_repo, artwork_repo) # ExhibitionService требует IExhibitionRepository и IArtworkRepository

    # Инициализируем фабрику плагинов сериализации и CLIConfig
    factory = SerializationPluginFactory()
    factory.initialize()
    cli_config = CLIConfig()
    
    return ServiceCollection(
        user_service=user_service,
        artwork_service=artwork_service,
        exhibition_service=exhibition_service,
        cli_config=cli_config,
        serialization_factory=factory
    )
