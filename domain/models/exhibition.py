from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Exhibition:
    id: int
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    artwork_ids: List[int] = field(default_factory=list)
    max_capacity: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

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

    def __eq__(self, other: object) -> bool:
        """Сравнивает выставки по id"""
        if not isinstance(other, Exhibition):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Хеширует выставку по id"""
        return hash(self.id)
