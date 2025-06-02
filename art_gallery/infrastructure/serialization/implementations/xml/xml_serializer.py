import xml.etree.ElementTree as ET
from typing import Any, Dict, List
from art_gallery.infrastructure.serialization.interfaces.ISerializer import ISerializer
from art_gallery.ui.exceptions.serialization_exceptions import SerializationError

class XmlSerializer(ISerializer):
    """Реализация сериализатора для формата XML"""
    
    def _dict_to_xml(self, parent: ET.Element, data: Any) -> None:
        """
        Рекурсивно преобразует словарь/список в XML элементы
        
        Args:
            parent: Родительский XML элемент
            data: Данные для преобразования
        """
        if isinstance(data, dict):
            for key, value in data.items():
                # Создаем элемент с именем ключа
                child = ET.SubElement(parent, str(key))
                if isinstance(value, (dict, list)):
                    self._dict_to_xml(child, value)
                else:
                    child.text = str(value)
        elif isinstance(data, list):
            for item in data:
                # Для списков создаем элемент 'item'
                child = ET.SubElement(parent, 'item')
                if isinstance(item, (dict, list)):
                    self._dict_to_xml(child, item)
                else:
                    child.text = str(item)
        else:
            parent.text = str(data)

    def serialize(self, data: Any) -> str:
        """
        Сериализует данные в XML строку
        
        Args:
            data: Данные для сериализации
            
        Returns:
            str: XML строка
            
        Raises:
            SerializationError: Если возникла ошибка при сериализации
        """
        try:
            root = ET.Element('root')
            self._dict_to_xml(root, data)
            return ET.tostring(root, encoding='unicode', method='xml')
        except Exception as e:
            raise SerializationError(f"Ошибка сериализации в XML: {str(e)}")

    def serialize_to_file(self, data: Any, filepath: str) -> None:
        """
        Сериализует данные и записывает их в XML файл
        
        Args:
            data: Данные для сериализации
            filepath (str): Путь к файлу для сохранения
            
        Raises:
            SerializationError: Если возникла ошибка при сериализации или записи
        """
        try:
            root = ET.Element('root')
            self._dict_to_xml(root, data)
            tree = ET.ElementTree(root)
            tree.write(filepath, encoding='utf-8', xml_declaration=True)
        except Exception as e:
            raise SerializationError(f"Ошибка записи в XML файл: {str(e)}")
