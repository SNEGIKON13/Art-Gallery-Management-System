import json
from typing import Any
from serialization.interfaces.IDeserializer import IDeserializer
from serialization.serialization_exceptions import DeserializationError

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
            Any: Десериализованные данные (пустой список, если файл не существует или пуст)
            
        Raises:
            DeserializationError: Если возникла ошибка при чтении или десериализации
        """
        import os
        
        # Проверяем существование файла
        if not os.path.exists(filepath):
            return []  # Возвращаем пустой список, если файл не существует
            
        # Проверяем, что файл не пустой
        if os.path.getsize(filepath) == 0:
            return []  # Возвращаем пустой список для пустого файла
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise DeserializationError(f"Ошибка формата JSON в файле {filepath}: {str(e)}")
        except Exception as e:
            raise DeserializationError(f"Ошибка чтения из JSON файла {filepath}: {str(e)}")
