from dataclasses import dataclass
from application.services.mocks.mock_user_service import MockUserService
from application.services.mocks.mock_artwork_service import MockArtworkService
from application.services.mocks.mock_exhibition_service import MockExhibitionService
from application.interfaces.user_service import IUserService
from application.interfaces.artwork_service import IArtworkService
from application.interfaces.exhibition_service import IExhibitionService

@dataclass
class ServiceCollection:
    user_service: IUserService
    artwork_service: IArtworkService
    exhibition_service: IExhibitionService

def create_mock_services() -> ServiceCollection:
    return ServiceCollection(
        user_service=MockUserService(),
        artwork_service=MockArtworkService(),
        exhibition_service=MockExhibitionService()
    )
