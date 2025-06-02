import pkg_resources
from typing import Dict, Type
from art_gallery.infrastructure.interfaces.serialization_plugin import ISerializationPlugin

import pkg_resources
from typing import Dict
from serialization.interfaces.ISerializer import ISerializer
from serialization.interfaces.IDeserializer import IDeserializer

class SerializationPluginFactory:
    """Фабрика для создания и управления плагинами сериализации и десериализации"""
    
    _serializers: Dict[str, ISerializer] = {}
    _deserializers: Dict[str, IDeserializer] = {}
    _supported_formats_cache: list[str] = []
    
    @classmethod
    def initialize(cls) -> None:
        """Инициализирует доступные плагины сериализации и десериализации"""
        cls._serializers.clear()
        cls._deserializers.clear()
        cls._supported_formats_cache.clear()

        print(f"[INFO] Initializing serialization plugins...")
        # Показываем путь к пакету pkg_resources для отладки
        print(f"[DEBUG] pkg_resources path: {pkg_resources.__file__}")
        
        loaded_serializer_formats = set()
        serializer_entry_points = list(pkg_resources.iter_entry_points('gallery.serialization'))
        print(f"[INFO] Found {len(serializer_entry_points)} serializer entry points")
        
        for entry_point in serializer_entry_points:
            try:
                print(f"[INFO] Loading serializer plugin: {entry_point.name} from {entry_point.module_name}")
                plugin_class = entry_point.load()
                instance = plugin_class()
                if isinstance(instance, ISerializer):
                    cls._serializers[entry_point.name] = instance
                    loaded_serializer_formats.add(entry_point.name)
                    print(f"[INFO] Successfully loaded serializer plugin: {entry_point.name}")
                else:
                    print(f"[WARN] Plugin {entry_point.name} from 'gallery.serialization' is not an ISerializer.")
            except Exception as e:
                print(f"[ERROR] Failed to load serializer plugin {entry_point.name}: {e}")
                import traceback
                traceback.print_exc()

        loaded_deserializer_formats = set()
        deserializer_entry_points = list(pkg_resources.iter_entry_points('gallery.deserialization'))
        print(f"[INFO] Found {len(deserializer_entry_points)} deserializer entry points")
        
        for entry_point in deserializer_entry_points:
            try:
                print(f"[INFO] Loading deserializer plugin: {entry_point.name} from {entry_point.module_name}")
                plugin_class = entry_point.load()
                instance = plugin_class()
                if isinstance(instance, IDeserializer):
                    cls._deserializers[entry_point.name] = instance
                    loaded_deserializer_formats.add(entry_point.name)
                    print(f"[INFO] Successfully loaded deserializer plugin: {entry_point.name}")
                else:
                    print(f"[WARN] Plugin {entry_point.name} from 'gallery.deserialization' is not an IDeserializer.")
            except Exception as e:
                print(f"[ERROR] Failed to load deserializer plugin {entry_point.name}: {e}")
                import traceback
                traceback.print_exc()
        
        # Supported formats are those available for BOTH serialization and deserialization
        cls._supported_formats_cache = list(loaded_serializer_formats.intersection(loaded_deserializer_formats))
        print(f"[INFO] Supported formats: {cls._supported_formats_cache}")
        if not cls._supported_formats_cache:
            print("[WARN] No common formats supported by both serializers and deserializers.") # Or log
            # Fallback: list all loaded serializer formats if no common ones, or handle as error
            # For now, let's keep it as intersection. Or, we might want separate lists.

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
