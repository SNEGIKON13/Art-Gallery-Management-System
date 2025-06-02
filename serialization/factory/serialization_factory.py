from enum import Enum, auto
from typing import Type, Dict, Tuple

from serialization.interfaces.ISerializer import ISerializer
from serialization.interfaces.IDeserializer import IDeserializer
from serialization.implementations.json.json_serializer import JsonSerializer
from serialization.implementations.json.json_deserializer import JsonDeserializer
from serialization.implementations.xml.xml_serializer import XmlSerializer
from serialization.implementations.xml.xml_deserializer import XmlDeserializer

class SerializationFormat(Enum):
    """Поддерживаемые форматы сериализации"""
    JSON = auto()
    XML = auto()

class SerializationFactory:
    """Фабрика для создания сериализаторов и десериализаторов"""
    
    _formats: Dict[SerializationFormat, Tuple[Type[ISerializer], Type[IDeserializer]]] = {
        SerializationFormat.JSON: (JsonSerializer, JsonDeserializer),
        SerializationFormat.XML: (XmlSerializer, XmlDeserializer)
    }
    
    @classmethod
    def create_serializer(cls, format: SerializationFormat) -> ISerializer:
        """
        Создает сериализатор для указанного формата
        
        Args:
            format (SerializationFormat): Формат сериализации
            
        Returns:
            ISerializer: Экземпляр сериализатора
            
        Raises:
            ValueError: Если формат не поддерживается
        """
        if format not in cls._formats:
            raise ValueError(f"Неподдерживаемый формат сериализации: {format}")
            
        serializer_class = cls._formats[format][0]
        return serializer_class()
        
    @classmethod
    def create_deserializer(cls, format: SerializationFormat) -> IDeserializer:
        """
        Создает десериализатор для указанного формата
        
        Args:
            format (SerializationFormat): Формат сериализации
            
        Returns:
            IDeserializer: Экземпляр десериализатора
            
        Raises:
            ValueError: Если формат не поддерживается
        """
        if format not in cls._formats:
            raise ValueError(f"Неподдерживаемый формат десериализации: {format}")
            
        deserializer_class = cls._formats[format][1]
        return deserializer_class()

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """
        Возвращает список поддерживаемых форматов
        
        Returns:
            list[str]: Список названий поддерживаемых форматов
        """
        return [format.name.lower() for format in SerializationFormat]
