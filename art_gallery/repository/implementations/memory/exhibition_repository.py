from typing import List
from datetime import datetime
from art_gallery.domain import Exhibition
from art_gallery.repository.interfaces.exhibition_repository import IExhibitionRepository
from art_gallery.repository.implementations.base_memory_repository import BaseMemoryRepository

class ExhibitionMemoryRepository(BaseMemoryRepository[Exhibition], IExhibitionRepository):
    def get_active(self) -> List[Exhibition]:
        now = datetime.now()
        return [exhibition for exhibition in self._items.values() 
                if exhibition.start_date <= now <= exhibition.end_date]

    def get_by_date_range(self, start: datetime, end: datetime) -> List[Exhibition]:
        return [exhibition for exhibition in self._items.values()
                if exhibition.start_date <= end and exhibition.end_date >= start]
