from typing import List, Optional, Dict
from datetime import datetime
from art_gallery.domain.exhibition import Exhibition
from art_gallery.application.interfaces.exhibition_service import IExhibitionService

class MockExhibitionService(IExhibitionService):
    def __init__(self):
        self._exhibitions: Dict[int, Exhibition] = {}
        self._next_id = 1

    def create_exhibition(self, title: str, description: str, 
                         start_date: datetime, end_date: datetime,
                         max_capacity: Optional[int] = None) -> Exhibition:
        exhibition = Exhibition(title=title, description=description,
                             start_date=start_date, end_date=end_date,
                             max_capacity=max_capacity)
        exhibition.id = self._next_id
        self._exhibitions[self._next_id] = exhibition
        self._next_id += 1
        return exhibition

    def update_exhibition(self, exhibition_id: int, title: Optional[str] = None,
                         description: Optional[str] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         max_capacity: Optional[int] = None) -> Exhibition:
        if exhibition_id not in self._exhibitions:
            raise ValueError(f"Exhibition {exhibition_id} not found")
            
        exhibition = self._exhibitions[exhibition_id]
        if title:
            exhibition.title = title
        if description:
            exhibition.description = description
        if start_date and end_date:
            exhibition.update_dates(start_date, end_date)
        if max_capacity is not None:
            exhibition.max_capacity = max_capacity
            
        return exhibition

    def delete_exhibition(self, exhibition_id: int) -> None:
        self._exhibitions.pop(exhibition_id, None)

    def add_artwork(self, exhibition_id: int, artwork_id: int) -> None:
        if exhibition_id not in self._exhibitions:
            raise ValueError(f"Exhibition {exhibition_id} not found")
        self._exhibitions[exhibition_id].add_artwork(artwork_id)

    def remove_artwork(self, exhibition_id: int, artwork_id: int) -> None:
        if exhibition_id not in self._exhibitions:
            raise ValueError(f"Exhibition {exhibition_id} not found")
        self._exhibitions[exhibition_id].remove_artwork(artwork_id)

    def get_exhibition(self, exhibition_id: int) -> Optional[Exhibition]:
        return self._exhibitions.get(exhibition_id)

    def get_all_exhibitions(self) -> List[Exhibition]:
        return list(self._exhibitions.values())

    def get_active_exhibitions(self) -> List[Exhibition]:
        now = datetime.now()
        return [ex for ex in self._exhibitions.values() if ex.is_active()]

    def check_availability(self, exhibition_id: int) -> bool:
        if exhibition_id not in self._exhibitions:
            raise ValueError(f"Exhibition {exhibition_id} not found")
        return self._exhibitions[exhibition_id].has_space()
        
    def add_imported_exhibition(self, title: str, description: str, 
                             start_date: datetime, end_date: datetime,
                             created_at: Optional[datetime] = None,
                             max_capacity: Optional[int] = None,
                             artwork_ids: Optional[List[int]] = None,
                             visitors: Optional[List[int]] = None,
                             id: Optional[int] = None) -> Exhibition:
        """
        Добавляет импортированную выставку с заданными значениями полей.
        """
        # Создаем выставку с указанными параметрами
        exhibition = Exhibition(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            created_at=created_at or datetime.now(),
            max_capacity=max_capacity
        )
        
        # Устанавливаем ID
        if id is not None:
            exhibition.id = id
            # Если существует выставка с таким ID, обновляем
            if id in self._exhibitions:
                # Сохраняем в словарь
                self._exhibitions[id] = exhibition
            else:
                # Добавляем с указанным ID
                self._exhibitions[id] = exhibition
                # Обновляем next_id если необходимо
                if id >= self._next_id:
                    self._next_id = id + 1
        else:
            # Если ID не задан, генерируем новый
            exhibition.id = self._next_id
            self._exhibitions[self._next_id] = exhibition
            self._next_id += 1
        
        # Добавляем экспонаты, если они указаны
        if artwork_ids:
            for artwork_id in artwork_ids:
                exhibition.add_artwork(artwork_id)
                
        # Добавляем посетителей, если они указаны
        if visitors:
            for visitor_id in visitors:
                exhibition.add_visitor(visitor_id)
                
        return exhibition
