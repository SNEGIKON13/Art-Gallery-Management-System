import json
from typing import Any
from serialization.interfaces.ISerializer import ISerializer
from serialization.serialization_exceptions import SerializationError

class JsonSerializer(ISerializer):
    """Реализация сериализатора для формата JSON"""
    
    def serialize(self, data: Any) -> str:
        """
        Сериализует данные в JSON строку
        
        Args:
            data: Данные для сериализации
            
        Returns:
            str: JSON строка
            
        Raises:
            SerializationError: Если возникла ошибка при сериализации
        """
        try:
            return json.dumps(data, indent=4, ensure_ascii=False)
        except Exception as e:
            raise SerializationError(f"Ошибка сериализации в JSON: {str(e)}")

    def serialize_to_file(self, data: Any, filepath: str) -> None:
        """
        Сериализует данные и записывает их в JSON файл
        
        Args:
            data: Данные для сериализации
            filepath (str): Путь к файлу для сохранения
            
        Raises:
            SerializationError: Если возникла ошибка при сериализации или записи
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            raise SerializationError(f"Ошибка записи в JSON файл: {str(e)}")
