import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from art_gallery.domain.models import Exhibition
from art_gallery.repository.interfaces.exhibition_repository import IExhibitionRepository
from art_gallery.repository.specifications.base_specification import Specification

class ExhibitionJsonRepository(IExhibitionRepository):
    def __init__(self, filepath: str):
        self._filepath = filepath
        # Создаем директорию, если нужно
        file_dir = os.path.dirname(self._filepath)
        if file_dir:
            os.makedirs(file_dir, exist_ok=True)
        
        self._exhibitions: List[Exhibition] = []
        self._load_data()

    def _load_data(self) -> None:
        if not os.path.exists(self._filepath) or os.path.getsize(self._filepath) == 0:
            self._exhibitions = []
            # Создаем пустой файл, если не существует
            with open(self._filepath, 'w', encoding='utf-8') as f:
                json.dump([], f)
            return
        
        try:
            with open(self._filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Загружаем выставки из данных
                loaded_exhibitions = []
                for exhibition_data in data:
                    try:
                        loaded_exhibitions.append(Exhibition.from_dict(exhibition_data))
                    except Exception as e:
                        print(f"Error deserializing exhibition: {e}")
                self._exhibitions = loaded_exhibitions
        except json.JSONDecodeError:
            print(f"Invalid JSON in {self._filepath}. Starting with empty exhibition list.")
            self._exhibitions = []
        except Exception as e:
            print(f"Error loading exhibitions: {e}")
            self._exhibitions = []

    def _save_data(self) -> None:
        try:
            with open(self._filepath, 'w', encoding='utf-8') as f:
                json.dump([exhibition.to_dict() for exhibition in self._exhibitions], f, indent=4, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Error saving exhibitions: {e}")

    def add(self, exhibition: Exhibition) -> Exhibition:
        # Добавляем выставку и сохраняем
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
        """
        Найти выставки, соответствующие спецификации
        """
        return [exhibition for exhibition in self._exhibitions if specification.is_satisfied_by(exhibition)]
        
    def get_active(self) -> List[Exhibition]:
        """
        Получить все активные выставки
        Активные выставки - это те, у которых текущая дата находится между датой начала и окончания
        """
        now = datetime.now()
        return [exhibition for exhibition in self._exhibitions 
                if exhibition.start_date <= now <= exhibition.end_date]
    
    def get_by_date_range(self, start: datetime, end: datetime) -> List[Exhibition]:
        """
        Получить выставки в заданном временном промежутке
        Возвращает выставки, которые пересекаются с заданным временным промежутком
        """
        return [exhibition for exhibition in self._exhibitions 
                if (exhibition.start_date <= end and exhibition.end_date >= start)]
        # Метод просто не делает ничего, если выставка не найдена
        # и возвращает None в соответствии с интерфейсом
