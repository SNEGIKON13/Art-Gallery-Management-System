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

    def deserialize_from_file(self, filepath: str) -> Any: # Возвращаемый тип Any, но фактически List[Dict[str, Any]]
        """
        Читает и десериализует данные из JSON файла.
        Возвращает пустой список, если файл не найден или пуст.
        
        Args:
            filepath (str): Путь к файлу для чтения
            
        Returns:
            List[Any]: Десериализованные данные (ожидается список словарей, совместимый с Any)
            
        Raises:
            DeserializationError: Если возникла ошибка при десериализации (кроме пустого/отсутствующего файла)
        """
        import os
        # import json # json уже импортирован на уровне модуля
        
        if not os.path.exists(filepath):
            return [] # Файл не существует
        
        try:
            # Сначала проверяем размер файла, чтобы избежать чтения больших пустых файлов
            if os.path.getsize(filepath) == 0:
                return [] # Файл пуст (по размеру)

            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if not content:
                    return [] # Файл содержит только пробелы или пуст после strip
                return json.loads(content) # Используем json.loads для строки
        except json.JSONDecodeError as e:
            # Если файл не пустой, но содержит невалидный JSON
            raise DeserializationError(f"Ошибка десериализации JSON из файла {filepath}: {str(e)}")
        except FileNotFoundError:
            # Эта ветка на случай, если файл удалили между os.path.exists и open, хотя маловероятно
            return []
        except Exception as e:
            # Прочие ошибки чтения/доступа, которые не являются JSONDecodeError
            raise DeserializationError(f"Ошибка чтения, доступа или другая ошибка при обработке файла {filepath}: {str(e)}")
