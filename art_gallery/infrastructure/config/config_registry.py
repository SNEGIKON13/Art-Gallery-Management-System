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
            self._cli_config = CLIConfig()
            self._storage_config = StorageConfig.from_env()
            
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
    
    def get(self, config_type: Type[T]) -> Optional[T]:
        """
        Получить конфигурацию по её типу.
        
        Args:
            config_type: Тип конфигурации (CLIConfig, StorageConfig, MinioConfig)
            
        Returns:
            Экземпляр запрошенной конфигурации или None, если не найден
        """
        if config_type == CLIConfig:
            return self._cli_config  # type: ignore
        elif config_type == StorageConfig:
            return self._storage_config  # type: ignore
        elif config_type == MinioConfig:
            return self._minio_config  # type: ignore
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
        
        if self._storage_config and self._storage_config.storage_type.lower() == "cloud":
            logging.info(f"MinIO Config: {'Loaded' if self._minio_config else 'Not loaded'}")
            if self._minio_config:
                # Не логируем секреты
                logging.info(f"  Endpoint: {self._minio_config.endpoint}")
                logging.info(f"  Default Bucket: {self._minio_config.default_bucket}")
                logging.info(f"  Secure: {self._minio_config.secure}")
        
        logging.info(f"Overall configuration validity: {self._is_valid}")
