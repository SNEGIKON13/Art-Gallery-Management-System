import xml.etree.ElementTree as ET
from typing import Any, Dict, List
from serialization.interfaces.IDeserializer import IDeserializer
from serialization.serialization_exceptions import DeserializationError

class XmlDeserializer(IDeserializer):
    """Реализация десериализатора для формата XML"""
    
    def _xml_to_dict(self, element: ET.Element) -> Any:
        """
        Рекурсивно преобразует XML элементы в словарь/список/значение
        
        Args:
            element: XML элемент
            
        Returns:
            Any: Преобразованные данные
        """
        # Если у элемента нет дочерних элементов, возвращаем его текст
        if len(element) == 0:
            return element.text if element.text else ""
        
        result: Dict[str, Any] = {}
        # Если все дочерние элементы имеют тег 'item', это список
        if all(child.tag == 'item' for child in element):
            return [self._xml_to_dict(child) for child in element]
        
        # Иначе это словарь
        for child in element:
            if child.tag in result:
                # Если тег уже существует, преобразуем значение в список
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(self._xml_to_dict(child))
            else:
                result[child.tag] = self._xml_to_dict(child)
        
        return result

    def deserialize(self, data: str) -> Any:
        """
        Десериализует данные из XML строки
        
        Args:
            data (str): XML строка для десериализации
            
        Returns:
            Any: Десериализованные данные
            
        Raises:
            DeserializationError: Если возникла ошибка при десериализации
        """
        try:
            root = ET.fromstring(data)
            return self._xml_to_dict(root)
        except Exception as e:
            raise DeserializationError(f"Ошибка десериализации из XML: {str(e)}")

    def deserialize_from_file(self, filepath: str) -> Any:
        """
        Читает и десериализует данные из XML файла
        
        Args:
            filepath (str): Путь к файлу для чтения
            
        Returns:
            Any: Десериализованные данные или пустой список, если файл не существует или пуст
        """
        import os
        try:
            # Проверяем существование файла и его размер
            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                print(f"[ИНФО] XML файл {filepath} не существует или пуст. Возвращаем пустой список.")
                return []
                
            tree = ET.parse(filepath)
            root = tree.getroot()
            result = self._xml_to_dict(root)
            
            # Если результат не список, а root пуст, возвращаем пустой список
            if not isinstance(result, list) and result == {}:
                return []
                
            return result
        except Exception as e:
            print(f"[ОШИБКА] При чтении XML файла {filepath}: {str(e)}")
            # В случае ошибки возвращаем пустой список вместо исключения
            return []
