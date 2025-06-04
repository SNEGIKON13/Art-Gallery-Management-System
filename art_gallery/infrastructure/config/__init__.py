"""Пакет конфигурации приложения Art Gallery Management System.

Этот пакет обеспечивает загрузку и управление конфигурацией из переменных окружения.
При импорте пакета автоматически загружаются переменные окружения из .env файла.
"""

import os
import logging

# Загрузка переменных окружения из .env файла
try:
    from dotenv import load_dotenv
    env_loaded = load_dotenv()
    if env_loaded:
        logging.info("Переменные окружения успешно загружены из .env файла")
    else:
        logging.warning("Файл .env не найден или пуст. Используются только системные переменные окружения.")
except ImportError:
    logging.warning("Библиотека python-dotenv не установлена. Переменные окружения из .env не загружены.")
    logging.warning("Для установки выполните: pip install python-dotenv")

# Импорт классов конфигурации
from .cli_config import CLIConfig
from .storage_config import StorageConfig
from .minio_config import MinioConfig
from .serialization_config import SerializationConfig
from .config_registry import ConfigRegistry
from .constants import *

__all__ = ['CLIConfig', 'StorageConfig', 'MinioConfig', 'SerializationConfig', 'ConfigRegistry']
