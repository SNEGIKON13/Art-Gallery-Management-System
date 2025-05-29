from dependency_injector import containers, providers
from repository.implementations.unit_of_work import UnitOfWork
from application.services.artwork_service import ArtworkService
from application.services.exhibition_service import ExhibitionService
from application.services.user_service import UserService

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    unit_of_work = providers.Singleton(UnitOfWork)
    
    artwork_service = providers.Factory(
        ArtworkService,
        unit_of_work=unit_of_work
    )
    
    exhibition_service = providers.Factory(
        ExhibitionService,
        unit_of_work=unit_of_work
    )
    
    user_service = providers.Factory(
        UserService,
        unit_of_work=unit_of_work
    )
