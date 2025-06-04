"""
Конфигурация сериализации данных
"""

import os
from dataclasses import dataclass
from .constants import DEFAULT_SERIALIZATION_FORMAT, SUPPORTED_SERIALIZATION_FORMATS


@dataclass
class SerializationConfig:
    """Конфигурация для механизма сериализации данных"""
    format: str = DEFAULT_SERIALIZATION_FORMAT
    
    @classmethod
    def from_env(cls) -> 'SerializationConfig':
        """
        Создает конфигурацию сериализации на основе переменных окружения.
        
        Returns:
            SerializationConfig: Объект конфигурации с загруженными значениями
        """
        format_value = os.environ.get('SERIALIZATION_FORMAT', DEFAULT_SERIALIZATION_FORMAT)
        return cls(format=format_value)
    
    def __post_init__(self):
        """Валидация конфигурации сериализации после инициализации."""
        if self.format not in SUPPORTED_SERIALIZATION_FORMATS:
            supported_formats = ', '.join(SUPPORTED_SERIALIZATION_FORMATS)
            raise ValueError(
                f"Неподдерживаемый формат сериализации: '{self.format}'. "
                f"Поддерживаемые форматы: {supported_formats}"
            )
