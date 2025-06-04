from datetime import datetime
from typing import List, Optional
from art_gallery.domain import Exhibition
from art_gallery.repository.interfaces.exhibition_repository import IExhibitionRepository
from art_gallery.repository.interfaces.artwork_repository import IArtworkRepository
from art_gallery.application.interfaces.exhibition_service import IExhibitionService
from art_gallery.application.validation.validators import BusinessRuleValidator

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
        
    def add_imported_exhibition(self, title: str, description: str, 
                             start_date: datetime, end_date: datetime,
                             created_at: Optional[datetime] = None,
                             max_capacity: Optional[int] = None,
                             artwork_ids: Optional[List[int]] = None,
                             visitors: Optional[List[int]] = None,
                             id: Optional[int] = None) -> Exhibition:
        """
        Добавляет импортированную выставку с заданными значениями полей.
        Отличие от create_exhibition в том, что позволяет устанавливать дополнительные поля, 
        такие как created_at, artwork_ids, visitors и id, что необходимо при импорте данных.
        """
        # Проверка бизнес-правил
        BusinessRuleValidator.validate_exhibition_dates(start_date, end_date)
        
        # Создаем объект с указанными параметрами
        exhibition = Exhibition(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            created_at=created_at or datetime.now(),
            max_capacity=max_capacity
        )
        
        # Устанавливаем ID, если он предоставлен
        if id is not None:
            exhibition.id = id
            
        # Добавляем экспонаты, если они есть
        if artwork_ids:
            for artwork_id in artwork_ids:
                # Проверяем существование экспоната при необходимости
                if self._artwork_repository and not self._artwork_repository.get_by_id(artwork_id):
                    # Пропускаем несуществующие экспонаты при импорте
                    continue
                exhibition.add_artwork(artwork_id)
                
        # Добавляем посетителей, если они есть
        if visitors:
            for visitor_id in visitors:
                exhibition.add_visitor(visitor_id)
                
        # Проверяем, существует ли уже выставка с таким ID
        if id is not None and self._exhibition_repository.get_by_id(id):
            # Если существует, выполняем обновление
            return self._exhibition_repository.update(exhibition)
        else:
            # Если не существует, добавляем новую
            return self._exhibition_repository.add(exhibition)
