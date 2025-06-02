from abc import ABC, abstractmethod
from typing import Any, Dict, List

class ISerializationPlugin(ABC):
    """Интерфейс для работы с плагином сериализации"""
    
    @abstractmethod
    def serialize(self, format: str, data: Any) -> str:
        """
        Сериализует данные в выбранный формат
        
        Args:
            format (str): Формат сериализации ('json' или 'xml')
            data: Данные для сериализации
            
        Returns:
            str: Сериализованные данные
        """
        pass
    
    @abstractmethod
    def deserialize(self, format: str, data: str) -> Any:
        """
        Десериализует данные из выбранного формата
        
        Args:
            format (str): Формат десериализации ('json' или 'xml')
            data (str): Строка для десериализации
            
        Returns:
            Any: Десериализованные данные
        """
        pass
    
    @abstractmethod
    def serialize_to_file(self, format: str, data: Any, filepath: str) -> None:
        """
        Сериализует данные в файл выбранного формата
        
        Args:
            format (str): Формат сериализации ('json' или 'xml')
            data: Данные для сериализации
            filepath (str): Путь к файлу
        """
        pass
    
    @abstractmethod
    def deserialize_from_file(self, format: str, filepath: str) -> Any:
        """
        Десериализует данные из файла выбранного формата
        
        Args:
            format (str): Формат десериализации ('json' или 'xml')
            filepath (str): Путь к файлу
            
        Returns:
            Any: Десериализованные данные
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Возвращает список поддерживаемых форматов
        
        Returns:
            List[str]: Список форматов
        """
        pass
