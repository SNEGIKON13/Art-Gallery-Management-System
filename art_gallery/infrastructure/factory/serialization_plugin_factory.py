import pkg_resources
from typing import Dict, Type
from art_gallery.infrastructure.interfaces.serialization_plugin import ISerializationPlugin

class SerializationPluginFactory:
    """Фабрика для создания и управления плагинами сериализации"""
    
    _plugins: Dict[str, ISerializationPlugin] = {}
    
    @classmethod
    def initialize(cls) -> None:
        """Инициализирует доступные плагины сериализации"""
        for entry_point in pkg_resources.iter_entry_points('gallery.serialization'):
            plugin_class = entry_point.load()
            cls._plugins[entry_point.name] = plugin_class()
    
    @classmethod
    def get_plugin(cls, format: str) -> ISerializationPlugin:
        """
        Возвращает плагин для указанного формата
        
        Args:
            format (str): Формат сериализации
            
        Returns:
            ISerializationPlugin: Плагин сериализации
            
        Raises:
            ValueError: Если формат не поддерживается
        """
        if format not in cls._plugins:
            raise ValueError(f"Неподдерживаемый формат сериализации: {format}")
        return cls._plugins[format]
    
    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """
        Возвращает список поддерживаемых форматов
        
        Returns:
            list[str]: Список форматов
        """
        return list(cls._plugins.keys())
