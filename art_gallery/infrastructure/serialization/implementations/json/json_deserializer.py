import json
from typing import Any
from art_gallery.infrastructure.serialization.interfaces.IDeserializer import IDeserializer
from art_gallery.ui.exceptions.serialization_exceptions import DeserializationError

class JsonDeserializer(IDeserializer):
    """Реализация десериализатора для формата JSON"""
    
    def deserialize(self, data: str) -> Any:
        """
        Десериализует данные из JSON строки
        
        Args:
            data (str): JSON строка для десериализации
            
        Returns:
            Any: Десериализованные данные
            
        Raises:
            DeserializationError: Если возникла ошибка при десериализации
        """
        try:
            return json.loads(data)
        except Exception as e:
            raise DeserializationError(f"Ошибка десериализации из JSON: {str(e)}")

    def deserialize_from_file(self, filepath: str) -> Any:
        """
        Читает и десериализует данные из JSON файла
        
        Args:
            filepath (str): Путь к файлу для чтения
            
        Returns:
            Any: Десериализованные данные
            
        Raises:
            DeserializationError: Если возникла ошибка при чтении или десериализации
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            raise DeserializationError(f"Ошибка чтения из JSON файла: {str(e)}")
