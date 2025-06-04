"""
Единый реестр конфигурации приложения.
Обеспечивает централизованный доступ ко всем настройкам и их валидацию при запуске.
"""
import os
import logging
from typing import Dict, Any, List, Optional, TypeVar, Type, Callable, Union
from dataclasses import dataclass, field

from art_gallery.infrastructure.config.cli_config import CLIConfig
from art_gallery.infrastructure.config.storage_config import StorageConfig
from art_gallery.infrastructure.config.minio_config import MinioConfig
from art_gallery.infrastructure.config.serialization_config import SerializationConfig
from art_gallery.infrastructure.config.constants import (
    DEFAULT_SERIALIZATION_FORMAT,
    SUPPORTED_SERIALIZATION_FORMATS
)

# Тип для аннотирования любого конфига
T = TypeVar('T')

class ConfigError(Exception):
    """Исключение при ошибке конфигурации"""
    pass

class MissingConfigError(ConfigError):
    """Исключение при отсутствии необходимой конфигурации"""
    pass

class InvalidConfigError(ConfigError):
    """Исключение при некорректной конфигурации"""
    pass

@dataclass
class ConfigItem:
    """Элемент конфигурации с метаданными для валидации"""
    key: str
    required: bool
    default_value: Any = None
    validator: Optional[Callable] = None
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class ConfigRegistry:
    """
    Единый реестр конфигурации приложения.
    Загружает, хранит и валидирует все настройки приложения.
    """
    
    # Единственный экземпляр (Singleton)
    _instance = None
    
    @staticmethod
    def update_env_variable(key: str, value: str) -> bool:
        """
        Обновляет переменную окружения в .env файле.
        
        Args:
            key: Имя переменной окружения
            value: Новое значение
            
        Returns:
            bool: True если обновление выполнено успешно
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        env_path = os.path.join(base_dir, '.env')
        
        if not os.path.exists(env_path):
            logging.warning(f"Cannot update environment variable: .env file not found at {env_path}")
            return False
            
        try:
            # Чтение текущего содержимого
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Обновление или добавление переменной
            updated = False
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith('#') and (line.startswith(f"{key}=") or line.startswith(f"{key} =")):
                    lines[i] = f"{key}={value}\n"
                    updated = True
                    break
            
            if not updated:
                # Добавление новой переменной в конец файла
                if lines and not lines[-1].endswith('\n'):
                    lines[-1] += '\n'
                lines.append(f"{key}={value}\n")
            
            # Запись обновлённого содержимого
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                
            logging.debug(f"Environment variable {key} updated in .env file")
            return True
        except Exception as e:
            logging.error(f"Error updating environment variable {key}: {str(e)}")
            return False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Инициализируем конфигурации
        self._cli_config: Optional[CLIConfig] = None
        self._storage_config: Optional[StorageConfig] = None
        self._minio_config: Optional[MinioConfig] = None
        self._serialization_config: Optional[SerializationConfig] = None
        
        # Словарь с результатами валидации
        self._validation_results: Dict[str, List[str]] = {}
        
        # Флаг успешной валидации
        self._is_valid = False
        
        # Определение требований к переменным окружения
        self._env_requirements = {
            # Переменные для хранилища
            "STORAGE_TYPE": ConfigItem(
                key="STORAGE_TYPE",
                required=True,
                default_value="local",
                validator=lambda x: x in ["local", "cloud"],
                description="Тип хранилища (local/cloud)",
            ),
            
            # Настройки сериализации
            "SERIALIZATION_FORMAT": ConfigItem(
                key="SERIALIZATION_FORMAT",
                required=False,
                default_value=DEFAULT_SERIALIZATION_FORMAT,
                validator=lambda x: x in SUPPORTED_SERIALIZATION_FORMATS,
                description="Формат сериализации данных (json, xml, yaml, pickle)",
            ),
            "LOCAL_STORAGE_PATH": ConfigItem(
                key="LOCAL_STORAGE_PATH",
                required=True,
                default_value="media/artworks",
                description="Путь к локальному хранилищу файлов",
            ),
            
            # MinIO конфигурация - требуется только если STORAGE_TYPE=cloud
            "MINIO_ENDPOINT": ConfigItem(
                key="MINIO_ENDPOINT", 
                required=False,
                default_value="localhost:9000",
                dependencies=["STORAGE_TYPE"],
                validator=lambda x, env: not (env["STORAGE_TYPE"] == "cloud") or x,
                description="MinIO endpoint (required if STORAGE_TYPE=cloud)",
            ),
            "MINIO_ACCESS_KEY": ConfigItem(
                key="MINIO_ACCESS_KEY",
                required=False,
                dependencies=["STORAGE_TYPE"],
                validator=lambda x, env: not (env["STORAGE_TYPE"] == "cloud") or x,
                description="MinIO access key (required if STORAGE_TYPE=cloud)",
            ),
            "MINIO_SECRET_KEY": ConfigItem(
                key="MINIO_SECRET_KEY",
                required=False,
                dependencies=["STORAGE_TYPE"],
                validator=lambda x, env: not (env["STORAGE_TYPE"] == "cloud") or x,
                description="MinIO secret key (required if STORAGE_TYPE=cloud)",
            ),
            "MINIO_USE_SSL": ConfigItem(
                key="MINIO_USE_SSL",
                required=False,
                default_value="0",
                validator=lambda x: x in ["0", "1", "true", "false", "True", "False"],
                description="Использовать SSL для соединения с MinIO (0/1)"
            ),
            "MINIO_DEFAULT_BUCKET": ConfigItem(
                key="MINIO_DEFAULT_BUCKET",
                required=False,
                default_value="gallery-media",
                dependencies=["STORAGE_TYPE"],
                description="Имя бакета MinIO по умолчанию (required if STORAGE_TYPE=cloud)",
            ),
        }
        
        self._initialized = True
    
    def load_configurations(self) -> bool:
        """
        Загружает все конфигурации и проводит их валидацию.
        
        Returns:
            bool: True если все конфигурации валидны, иначе False
        """
        try:
            # Валидируем переменные окружения
            self._validate_environment_variables()
            
            # Загружаем конфигурации из окружения
            self._cli_config = CLIConfig.from_env()
            self._storage_config = StorageConfig.from_env()
            self._serialization_config = SerializationConfig.from_env()
            
            # Загружаем MinIO конфигурацию если нужно
            if self._storage_config.storage_type.lower() == "cloud":
                try:
                    self._minio_config = MinioConfig.from_env()
                except ValueError as e:
                    raise InvalidConfigError(f"Invalid MinIO configuration: {str(e)}")
            
            # Проверяем совместимость настроек
            self._validate_config_compatibility()
            
            # Если дошли до этой точки, валидация успешна
            self._is_valid = True
            return True
            
        except ConfigError as e:
            logging.error(f"Configuration error: {str(e)}")
            self._is_valid = False
            return False
    
    def _validate_environment_variables(self) -> None:
        """
        Проверяет наличие и корректность переменных окружения.
        
        Raises:
            MissingConfigError: Если отсутствует обязательная переменная
            InvalidConfigError: Если переменная имеет некорректное значение
        """
        # Собираем все переменные окружения
        env_vars = {}
        for key in self._env_requirements:
            config_item = self._env_requirements[key]
            value = os.getenv(key, config_item.default_value)
            env_vars[key] = value
            
        # Проверяем обязательные переменные
        for key, config_item in self._env_requirements.items():
            value = env_vars.get(key)
            
            # Проверяем наличие обязательных переменных
            if config_item.required and value is None:
                raise MissingConfigError(f"Missing required environment variable: {key}")
            
            # Проверяем валидность через функцию-валидатор
            if config_item.validator and value is not None:
                try:
                    if 'env' in config_item.validator.__code__.co_varnames:
                        # Валидатор с зависимостями
                        valid = config_item.validator(value, env_vars)
                    else:
                        # Простой валидатор
                        valid = config_item.validator(value)
                    
                    if not valid:
                        raise InvalidConfigError(
                            f"Invalid value for {key}: {value}. {config_item.description}"
                        )
                except Exception as e:
                    if not isinstance(e, InvalidConfigError):
                        raise InvalidConfigError(
                            f"Error validating {key}: {str(e)}"
                        )
                    raise
    
    def _validate_config_compatibility(self) -> None:
        """
        Проверяет совместимость разных конфигураций.
        
        Raises:
            InvalidConfigError: Если конфигурации несовместимы
        """
        # Проверка совместимости storage_type и minio_config
        if self._storage_config is not None and self._storage_config.storage_type.lower() == "cloud" and self._minio_config is None:
            raise InvalidConfigError(
                "Storage type is set to 'cloud' but MinIO configuration is not available"
            )
    
    def get_cli_config(self) -> CLIConfig:
        """Получить конфигурацию CLI"""
        if self._cli_config is None:
            raise MissingConfigError("CLI configuration is not loaded")
        return self._cli_config
    
    def get_storage_config(self) -> StorageConfig:
        """Получить конфигурацию хранилища"""
        if self._storage_config is None:
            raise MissingConfigError("Storage configuration is not loaded")
        return self._storage_config
    
    def get_minio_config(self) -> Optional[MinioConfig]:
        """Получить конфигурацию MinIO (если используется)"""
        return self._minio_config
    
    def get_serialization_config(self) -> SerializationConfig:
        """Получить конфигурацию сериализации"""
        if self._serialization_config is None:
            raise MissingConfigError("Serialization configuration is not loaded")
        return self._serialization_config
    
    def get(self, config_type: Type[T]) -> Optional[T]:
        """
        Получить конфигурацию по её типу.
        
        Args:
            config_type: Тип конфигурации (CLIConfig, StorageConfig, MinioConfig, SerializationConfig)
            
        Returns:
            Экземпляр запрошенной конфигурации или None, если не найден
        """
        if config_type == CLIConfig:
            return self._cli_config  # type: ignore
        elif config_type == StorageConfig:
            return self._storage_config  # type: ignore
        elif config_type == MinioConfig:
            return self._minio_config  # type: ignore
        elif config_type == SerializationConfig:
            return self._serialization_config  # type: ignore
        else:
            return None
    
    def is_valid(self) -> bool:
        """
        Проверить, что все конфигурации валидны.
        
        Returns:
            bool: True если конфигурации валидны, иначе False
        """
        return self._is_valid
    
    def print_configuration_status(self) -> None:
        """Выводит статус конфигурации в лог"""
        logging.info("Configuration status:")
        logging.info(f"CLI Config: {'Loaded' if self._cli_config else 'Not loaded'}")
        logging.info(f"Storage Config: {'Loaded' if self._storage_config else 'Not loaded'}")
        logging.info(f"Serialization Config: {'Loaded' if self._serialization_config else 'Not loaded'}")
        
        if self._serialization_config:
            logging.info(f"  Format: {self._serialization_config.format}")
        
        if self._storage_config and self._storage_config.storage_type.lower() == "cloud":
            logging.info(f"MinIO Config: {'Loaded' if self._minio_config else 'Not loaded'}")
            if self._minio_config:
                # Не логируем секреты
                logging.info(f"  Endpoint: {self._minio_config.endpoint}")
                logging.info(f"  Default Bucket: {self._minio_config.default_bucket}")
                logging.info(f"  Secure: {self._minio_config.secure}")
        
        logging.info(f"Overall configuration validity: {self._is_valid}")
