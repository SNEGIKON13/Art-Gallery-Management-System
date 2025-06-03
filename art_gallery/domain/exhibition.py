from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from art_gallery.domain.base_entity import BaseEntity

@dataclass
class Exhibition(BaseEntity):
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    created_at: datetime = field(default_factory=datetime.now)
    artwork_ids: List[int] = field(default_factory=list)
    max_capacity: Optional[int] = None
    visitors: set[int] = field(default_factory=set)

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not self.title or len(self.title) < 1:
            raise ValueError("Title cannot be empty")
        if not self.description:
            raise ValueError("Description cannot be empty")
        if self.start_date > self.end_date:
            raise ValueError("End date must be after start date")
        if self.max_capacity is not None and self.max_capacity < 0:
            raise ValueError("Max capacity cannot be negative")

    def add_artwork(self, artwork_id: int) -> None:
        """Добавляет экспонат в выставку"""
        if artwork_id not in self.artwork_ids:
            self.artwork_ids.append(artwork_id)

    def remove_artwork(self, artwork_id: int) -> None:
        """Удаляет экспонат из выставки"""
        if artwork_id in self.artwork_ids:
            self.artwork_ids.remove(artwork_id)

    def is_active(self) -> bool:
        """Проверяет, активна ли выставка в текущий момент"""
        now = datetime.now()
        return self.start_date <= now <= self.end_date

    def has_space(self) -> bool:
        """Проверяет, есть ли свободные места на выставке"""
        return self.max_capacity is None or len(self.artwork_ids) < self.max_capacity

    def update_dates(self, start_date: datetime, end_date: datetime) -> None:
        """Обновляет даты проведения выставки"""
        if start_date > end_date:
            raise ValueError("End date must be after start date")
        self.start_date = start_date
        self.end_date = end_date

    def contains_artwork(self, artwork_id: int) -> bool:
        """Проверяет, содержит ли выставка указанный экспонат"""
        return artwork_id in self.artwork_ids

    def add_visitor(self, visitor_id: int) -> None:
        """Добавляет посетителя на выставку"""
        self.visitors.add(visitor_id)

    def remove_visitor(self, visitor_id: int) -> None:
        """Удаляет посетителя с выставки"""
        self.visitors.discard(visitor_id)

    def get_visitor_count(self) -> int:
        """Возвращает количество посетителей"""
        return len(self.visitors)

    def _get_entity_data(self) -> Dict[str, Any]:
        """Получает данные выставки для сериализации"""
        return {
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'artwork_ids': self.artwork_ids,
            'max_capacity': self.max_capacity,
            'visitors': list(self.visitors)  # Преобразуем set в list для сериализации
        }
        
    def clone(self) -> 'Exhibition':
        """Создает глубокую копию объекта"""
        exhibition = Exhibition(
            title=self.title,
            description=self.description,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        exhibition.created_at = self.created_at
        exhibition.artwork_ids = self.artwork_ids.copy()  # Копируем список
        exhibition.max_capacity = self.max_capacity
        exhibition.visitors = self.visitors.copy()  # Копируем множество
        exhibition.id = self.id
        return exhibition
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Exhibition':
        """Создает объект Exhibition из словаря"""
        # Обработка обязательных полей
        title = data['title']
        description = data['description']
        
        # Обработка дат начала и окончания выставки
        start_date_str = data['start_date']
        end_date_str = data['end_date']
        
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
        
        # Обработка даты создания
        created_at_str = data.get('created_at')
        created_at = datetime.fromisoformat(created_at_str) if created_at_str else datetime.now()
        
        # Обработка опциональных полей
        max_capacity = data.get('max_capacity')
        
        # Обработка списка идентификаторов экспонатов
        artwork_ids = data.get('artwork_ids', [])
        
        # Обработка посетителей - преобразуем список в множество
        visitors_list = data.get('visitors', [])
        visitors_set = set(visitors_list) if visitors_list else set()
        
        # Создание объекта
        exhibition = cls(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            created_at=created_at,
            max_capacity=max_capacity
        )
        
        # Установка ID, если он есть в данных и валидный
        if 'id' in data:
            try:
                id_value = int(data['id'])
                if id_value > 0:
                    exhibition.id = id_value
            except (ValueError, TypeError):
                # Если ID не может быть преобразован в int или невалидный, игнорируем его
                pass
        
        # Добавление экспонатов и посетителей после создания объекта
        if artwork_ids:
            exhibition.artwork_ids = artwork_ids  # Можем напрямую присвоить список
        
        if visitors_set:
            exhibition.visitors = visitors_set  # Присваиваем множество
            
        return exhibition

    def __eq__(self, other: object) -> bool:
        """Сравнивает выставки по id"""
        if not isinstance(other, Exhibition):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Хеширует выставку по id"""
        return hash(self.id)
