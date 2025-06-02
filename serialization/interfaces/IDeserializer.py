from abc import ABC, abstractmethod
from typing import Any

class IDeserializer(ABC):
    """Базовый интерфейс для десериализации данных"""
    
    @abstractmethod
    def deserialize(self, data: str) -> Any:
        """
        Десериализует данные из строкового формата
        
        Args:
            data (str): Строка для десериализации
            
        Returns:
            Any: Десериализованные данные
            
        Raises:
            DeserializationError: Если возникла ошибка при десериализации
        """
        pass

    @abstractmethod
    def deserialize_from_file(self, filepath: str) -> Any:
        """
        Читает и десериализует данные из файла
        
        Args:
            filepath (str): Путь к файлу для чтения
            
        Returns:
            Any: Десериализованные данные
            
        Raises:
            DeserializationError: Если возникла ошибка при чтении или десериализации
        """
        pass
