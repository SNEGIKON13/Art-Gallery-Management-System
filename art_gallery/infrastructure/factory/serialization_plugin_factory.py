import pkg_resources
from typing import Dict, Type, Optional
from art_gallery.infrastructure.interfaces.serialization_plugin import ISerializationPlugin
from serialization.interfaces.ISerializer import ISerializer
from serialization.interfaces.IDeserializer import IDeserializer

class SerializationPluginFactory:
    """Фабрика для создания и управления плагинами сериализации и десериализации"""
    
    _serializers: Dict[str, ISerializer] = {}
    _deserializers: Dict[str, IDeserializer] = {}
    _supported_formats_cache: list[str] = []
    _verbose: bool = False  # Флаг для контроля вывода отладочных сообщений
    
    @classmethod
    def set_verbose(cls, verbose: bool) -> None:
        """Установить режим подробного вывода сообщений"""
        cls._verbose = verbose
    
    @classmethod
    def _log(cls, message: str, level: str = "INFO") -> None:
        """Выводит сообщение, если включен режим подробного вывода"""
        if cls._verbose or level in ["ERROR", "WARN"]:
            print(f"[{level}] {message}")
    
    @classmethod
    def initialize(cls, verbose: bool = False) -> None:
        """Инициализирует доступные плагины сериализации и десериализации"""
        cls._verbose = verbose
        cls._serializers.clear()
        cls._deserializers.clear()
        cls._supported_formats_cache.clear()

        cls._log("Initializing serialization plugins...")
        # Показываем путь к пакету pkg_resources для отладки
        cls._log(f"pkg_resources path: {pkg_resources.__file__}", "DEBUG")
        
        loaded_serializer_formats = set()
        serializer_entry_points = list(pkg_resources.iter_entry_points('gallery.serialization'))
        cls._log(f"Found {len(serializer_entry_points)} serializer entry points")
        
        for entry_point in serializer_entry_points:
            try:
                cls._log(f"Loading serializer plugin: {entry_point.name} from {entry_point.module_name}")
                plugin_class = entry_point.load()
                instance = plugin_class()
                if isinstance(instance, ISerializer):
                    cls._serializers[entry_point.name] = instance
                    loaded_serializer_formats.add(entry_point.name)
                    cls._log(f"Successfully loaded serializer plugin: {entry_point.name}")
                else:
                    cls._log(f"Plugin {entry_point.name} from 'gallery.serialization' is not an ISerializer.", "WARN")
            except Exception as e:
                cls._log(f"Failed to load serializer plugin {entry_point.name}: {e}", "ERROR")
                if cls._verbose:
                    import traceback
                    traceback.print_exc()

        loaded_deserializer_formats = set()
        deserializer_entry_points = list(pkg_resources.iter_entry_points('gallery.deserialization'))
        cls._log(f"Found {len(deserializer_entry_points)} deserializer entry points")
        
        for entry_point in deserializer_entry_points:
            try:
                cls._log(f"Loading deserializer plugin: {entry_point.name} from {entry_point.module_name}")
                plugin_class = entry_point.load()
                instance = plugin_class()
                if isinstance(instance, IDeserializer):
                    cls._deserializers[entry_point.name] = instance
                    loaded_deserializer_formats.add(entry_point.name)
                    cls._log(f"Successfully loaded deserializer plugin: {entry_point.name}")
                else:
                    cls._log(f"Plugin {entry_point.name} from 'gallery.deserialization' is not an IDeserializer.", "WARN")
            except Exception as e:
                cls._log(f"Failed to load deserializer plugin {entry_point.name}: {e}", "ERROR")
                if cls._verbose:
                    import traceback
                    traceback.print_exc()
        
        # Supported formats are those available for BOTH serialization and deserialization
        cls._supported_formats_cache = list(loaded_serializer_formats.intersection(loaded_deserializer_formats))
        cls._log(f"Supported formats: {cls._supported_formats_cache}")
        if not cls._supported_formats_cache:
            cls._log("No common formats supported by both serializers and deserializers.", "WARN")

    @classmethod
    def get_serializer(cls, format_name: str) -> ISerializer:
        """
        Возвращает плагин сериализатора для указанного формата.
        """
        if not cls._serializers: # Ensure initialized if called before app startup sequence
            cls.initialize()
        if format_name not in cls._serializers:
            raise ValueError(f"Неподдерживаемый формат для сериализации: {format_name}. Доступные: {list(cls._serializers.keys())}")
        return cls._serializers[format_name]

    @classmethod
    def create_serializer(cls, format_name: str) -> ISerializer:
        """
        Возвращает плагин сериализатора для указанного формата.
        Синоним для get_serializer для совместимости с API.
        """
        return cls.get_serializer(format_name)

    @classmethod
    def get_deserializer(cls, format_name: str) -> IDeserializer:
        """
        Возвращает плагин десериализатора для указанного формата.
        """
        if not cls._deserializers: # Ensure initialized
            cls.initialize()
        if format_name not in cls._deserializers:
            raise ValueError(f"Неподдерживаемый формат для десериализации: {format_name}. Доступные: {list(cls._deserializers.keys())}")
        return cls._deserializers[format_name]

    @classmethod
    def create_deserializer(cls, format_name: str) -> IDeserializer:
        """
        Возвращает плагин десериализатора для указанного формата.
        Синоним для get_deserializer для совместимости с API.
        """
        return cls.get_deserializer(format_name)
    
    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """
        Возвращает список форматов, поддерживаемых И для сериализации, И для десериализации.
        """
        if not cls._supported_formats_cache and (not cls._serializers and not cls._deserializers): # Ensure initialized
            cls.initialize()
        return cls._supported_formats_cache
