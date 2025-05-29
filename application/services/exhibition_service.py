from datetime import datetime
from typing import List, Optional
from domain.models import Exhibition
from repository.interfaces.exhibition_repository import IExhibitionRepository
from repository.interfaces.artwork_repository import IArtworkRepository
from application.interfaces.exhibition_service import IExhibitionService
from application.validation.validators import BusinessRuleValidator

class ExhibitionService(IExhibitionService):
    def __init__(self, 
                 exhibition_repository: IExhibitionRepository,
                 artwork_repository: IArtworkRepository):
        self._exhibition_repository = exhibition_repository
        self._artwork_repository = artwork_repository

    def create_exhibition(self, title: str, description: str,
                         start_date: datetime, end_date: datetime,
                         max_capacity: Optional[int] = None) -> Exhibition:
        BusinessRuleValidator.validate_exhibition_dates(start_date, end_date)
        
        exhibition = Exhibition(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            max_capacity=max_capacity
        )
        return self._exhibition_repository.add(exhibition)

    def update_exhibition(self, exhibition_id: int, title: Optional[str] = None,
                         description: Optional[str] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         max_capacity: Optional[int] = None) -> Exhibition:
        exhibition = self._exhibition_repository.get_by_id(exhibition_id)
        if not exhibition:
            raise ValueError(f"Exhibition with id {exhibition_id} not found")

        if title is not None:
            exhibition.title = title
        if description is not None:
            exhibition.description = description
        if start_date and end_date:
            exhibition.update_dates(start_date, end_date)
        elif start_date:
            exhibition.update_dates(start_date, exhibition.end_date)
        elif end_date:
            exhibition.update_dates(exhibition.start_date, end_date)
        if max_capacity is not None:
            exhibition.max_capacity = max_capacity

        return self._exhibition_repository.update(exhibition)

    def delete_exhibition(self, exhibition_id: int) -> None:
        if not self._exhibition_repository.get_by_id(exhibition_id):
            raise ValueError(f"Exhibition with id {exhibition_id} not found")
        self._exhibition_repository.delete(exhibition_id)

    def add_artwork(self, exhibition_id: int, artwork_id: int) -> None:
        exhibition = self._exhibition_repository.get_by_id(exhibition_id)
        if not exhibition:
            raise ValueError(f"Exhibition with id {exhibition_id} not found")

        artwork = self._artwork_repository.get_by_id(artwork_id)
        if not artwork:
            raise ValueError(f"Artwork with id {artwork_id} not found")

        BusinessRuleValidator.validate_exhibition_capacity(
            exhibition, 
            exhibition.artwork_ids + [artwork_id]
        )

        exhibition.add_artwork(artwork_id)
        self._exhibition_repository.update(exhibition)

    def remove_artwork(self, exhibition_id: int, artwork_id: int) -> None:
        exhibition = self._exhibition_repository.get_by_id(exhibition_id)
        if not exhibition:
            raise ValueError(f"Exhibition with id {exhibition_id} not found")

        if not exhibition.contains_artwork(artwork_id):
            raise ValueError(f"Artwork with id {artwork_id} not found in exhibition")

        exhibition.remove_artwork(artwork_id)
        self._exhibition_repository.update(exhibition)

    def get_exhibition(self, exhibition_id: int) -> Optional[Exhibition]:
        return self._exhibition_repository.get_by_id(exhibition_id)

    def get_all_exhibitions(self) -> List[Exhibition]:
        return self._exhibition_repository.get_all()

    def get_active_exhibitions(self) -> List[Exhibition]:
        return self._exhibition_repository.get_active()

    def check_availability(self, exhibition_id: int) -> bool:
        exhibition = self._exhibition_repository.get_by_id(exhibition_id)
        if not exhibition:
            raise ValueError(f"Exhibition with id {exhibition_id} not found")
        return exhibition.has_space()
