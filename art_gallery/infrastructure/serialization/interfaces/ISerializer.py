from abc import ABC, abstractmethod
from typing import Any

class ISerializer(ABC):
    """Базовый интерфейс для сериализации данных"""
    
    @abstractmethod
    def serialize(self, data: Any) -> str:
        """
        Сериализует данные в строковый формат
        
        Args:
            data: Данные для сериализации (dict, list, или любой другой тип)
            
        Returns:
            str: Сериализованные данные в виде строки
            
        Raises:
            SerializationError: Если возникла ошибка при сериализации
        """
        pass

    @abstractmethod
    def serialize_to_file(self, data: Any, filepath: str) -> None:
        """
        Сериализует данные и записывает их в файл
        
        Args:
            data: Данные для сериализации
            filepath (str): Путь к файлу для сохранения
            
        Raises:
            SerializationError: Если возникла ошибка при сериализации или записи
        """
        pass
