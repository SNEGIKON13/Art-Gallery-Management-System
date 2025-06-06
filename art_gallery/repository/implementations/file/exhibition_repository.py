import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from art_gallery.domain import Exhibition
from art_gallery.repository.interfaces.exhibition_repository import IExhibitionRepository
from art_gallery.repository.specifications.base_specification import Specification
from serialization.interfaces.ISerializer import ISerializer
from serialization.interfaces.IDeserializer import IDeserializer

class ExhibitionFileRepository(IExhibitionRepository):
    def __init__(self, filepath: str, serializer: ISerializer, deserializer: IDeserializer):
        self._filepath = filepath
        self._serializer = serializer  # Сериализатор из плагина
        self._deserializer = deserializer  # Десериализатор из плагина
        
        # Создаем директорию, если нужно
        file_dir = os.path.dirname(self._filepath)
        if file_dir:
            os.makedirs(file_dir, exist_ok=True)
        
        self._exhibitions: List[Exhibition] = []
        self._load_data()

    def _load_data(self) -> None:
        try:
            # Используем десериализатор из плагина
            list_of_dicts = self._deserializer.deserialize_from_file(self._filepath)
            loaded_exhibitions = []
            for exhibition_data_dict in list_of_dicts:
                try:
                    loaded_exhibitions.append(Exhibition.from_dict(exhibition_data_dict))
                except Exception as e:
                    print(f"Error creating Exhibition from dict: {exhibition_data_dict}, error: {e}")
                    # TODO: Заменить на логирование
            self._exhibitions = loaded_exhibitions
        except Exception as e:
            # В случае ошибки считаем, что данных нет
            print(f"Error loading data from {self._filepath} using deserializer: {e}")
            # TODO: Заменить на логирование
            self._exhibitions = []

    def _save_data(self) -> None:
        try:
            # Используем сериализатор из плагина
            data_to_serialize = [exhibition.to_dict() for exhibition in self._exhibitions]
            self._serializer.serialize_to_file(data_to_serialize, self._filepath)
        except Exception as e:
            print(f"Error saving data to {self._filepath} using serializer: {e}")
            # TODO: Заменить на логирование

    def add(self, exhibition: Exhibition) -> Exhibition:
        # Добавляем выставку и сохраняем
        if not exhibition.id:
            # Генерация ID для нового объекта (всегда положительный)
            if not self._exhibitions:
                new_id = 1  # Начинаем с 1, т.к. BaseEntity требует ID > 0
            else:
                # Находим максимальный ID и увеличиваем на 1
                existing_ids = [e.id for e in self._exhibitions if hasattr(e, 'id') and e.id is not None]
                if not existing_ids:
                    new_id = 1  # Начинаем с 1
                else:
                    new_id = max(existing_ids) + 1
            exhibition.id = new_id
        
        self._exhibitions.append(exhibition)
        self._save_data()
        return exhibition
        
    def get_by_id(self, exhibition_id: int) -> Optional[Exhibition]:
        return next((exhibition for exhibition in self._exhibitions if exhibition.id == exhibition_id), None)
        
    def get_all(self) -> List[Exhibition]:
        return list(self._exhibitions)
        
    def update(self, exhibition_to_update: Exhibition) -> Exhibition:
        for i, exhibition in enumerate(self._exhibitions):
            if exhibition.id == exhibition_to_update.id:
                self._exhibitions[i] = exhibition_to_update
                self._save_data()
                return exhibition_to_update
        raise ValueError(f"Exhibition with id {exhibition_to_update.id} not found.")
        
    def delete(self, exhibition_id: int) -> None:
        exhibition = self.get_by_id(exhibition_id)
        if exhibition:
            self._exhibitions.remove(exhibition)
            self._save_data()
            
    def find(self, specification: Specification[Exhibition]) -> List[Exhibition]:
        return [exhibition for exhibition in self._exhibitions if specification.is_satisfied_by(exhibition)]

    def get_active(self) -> List[Exhibition]:
        """
        Получить все активные выставки
        Активные выставки - это те, у которых текущая дата находится между датой начала и окончания
        Returns:
            List[Exhibition]: список активных выставок
        """
        now = datetime.now()
        return [exhibition for exhibition in self._exhibitions 
                if exhibition.start_date <= now <= exhibition.end_date]
    
    def get_by_date_range(self, start: datetime, end: datetime) -> List[Exhibition]:
        """
        Получить выставки в заданном временном промежутке
        Возвращает выставки, которые пересекаются с заданным временным промежутком
        Args:
            start (datetime): дата начала промежутка
            end (datetime): дата окончания промежутка
        Returns:
            List[Exhibition]: список выставок в данном промежутке
        """
        return [exhibition for exhibition in self._exhibitions 
                if (exhibition.start_date <= end and exhibition.end_date >= start)]
                
    def get_by_title(self, title: str) -> List[Exhibition]:
        """
        Получить выставки по названию
        Args:
            title (str): название выставки
        Returns:
            List[Exhibition]: список выставок с указанным названием
        """
        return [ex for ex in self._exhibitions if ex.title.lower() == title.lower()]
