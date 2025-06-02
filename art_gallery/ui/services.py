from dataclasses import dataclass
from art_gallery.application.services.mocks.mock_user_service import MockUserService
from art_gallery.application.services.mocks.mock_artwork_service import MockArtworkService
from art_gallery.application.services.mocks.mock_exhibition_service import MockExhibitionService
from art_gallery.application.interfaces.user_service import IUserService
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.application.interfaces.exhibition_service import IExhibitionService
from art_gallery.infrastructure.config.cli_config import CLIConfig
from art_gallery.infrastructure.factory.serialization_plugin_factory import SerializationPluginFactory

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
