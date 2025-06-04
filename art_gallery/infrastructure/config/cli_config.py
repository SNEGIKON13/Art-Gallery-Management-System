from dataclasses import dataclass, field
from typing import Dict, Optional
import os

from .constants import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    DEFAULT_DEBUG_MODE
)

@dataclass
class CLIConfig:
    """Конфигурация для CLI приложения"""
    # Символ приглашения к вводу
    prompt_symbol: str = "> "
    
    # Параметры работы CLI
    max_retries: int = DEFAULT_MAX_RETRIES
    timeout: int = DEFAULT_TIMEOUT
    debug_mode: bool = DEFAULT_DEBUG_MODE
    
    # ANSI коды цветов
    colors: Dict[str, str] = field(default_factory=dict)
    
    # Формат сообщений
    message_format: Dict[str, str] = field(default_factory=dict)
    
    # Путь к медиа файлам
    base_media_path: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'CLIConfig':
        """Создает конфигурацию CLI из переменных окружения"""
        # Получение значений из переменных окружения
        max_retries_str = os.getenv('CLI_MAX_RETRIES', str(DEFAULT_MAX_RETRIES))
        timeout_str = os.getenv('CLI_TIMEOUT', str(DEFAULT_TIMEOUT))
        debug_mode_str = os.getenv('CLI_DEBUG_MODE', str(int(DEFAULT_DEBUG_MODE)))
        prompt_symbol = os.getenv('CLI_PROMPT_SYMBOL', "> ")
        
        # Преобразование строковых значений к нужным типам
        try:
            max_retries = int(max_retries_str)
        except ValueError:
            max_retries = DEFAULT_MAX_RETRIES
            
        try:
            timeout = int(timeout_str)
        except ValueError:
            timeout = DEFAULT_TIMEOUT
            
        debug_mode = debug_mode_str.lower() in ('true', '1', 'yes')
        
        return cls(
            max_retries=max_retries,
            timeout=timeout,
            debug_mode=debug_mode,
            prompt_symbol=prompt_symbol
        )
        
    def __post_init__(self) -> None:
        """Валидация и инициализация после создания экземпляра"""
        # Валидация значений
        if self.max_retries < 0:
            raise ValueError(f"Количество повторных попыток не может быть отрицательным: {self.max_retries}")
            
        if self.timeout <= 0:
            raise ValueError(f"Таймаут должен быть положительным числом: {self.timeout}")
        
        # Инициализация путей
        if self.base_media_path is None:
            # Путь к корню проекта
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            # Путь к папке art_gallery/media
            self.base_media_path = os.path.join(project_root, "art_gallery", "media")
            
            # Создаем директории если их нет
            media_dirs = ["paintings", "sculptures", "photographs"]
            for dir_name in media_dirs:
                dir_path = os.path.join(self.base_media_path, dir_name)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)


        if not self.colors:
            self.colors = {
                "error": "\033[91m",  # Красный
                "success": "\033[92m",  # Зеленый
                "warning": "\033[93m",  # Желтый
                "info": "\033[94m",     # Синий
                "reset": "\033[0m"      # Сброс цвета
            }
        
        if not self.message_format:
            self.message_format = {
                "error": "[ERROR] {}",
                "success": "[SUCCESS] {}",
                "warning": "[WARNING] {}",
                "info": "[INFO] {}"
            }
    
    def format_message(self, message: str, message_type: str = "info") -> str:
        """Форматирует сообщение с цветом и префиксом"""
        color = self.colors.get(message_type, self.colors["reset"])
        format_str = self.message_format.get(message_type, "{}")
        return f"{color}{format_str}{self.colors['reset']}".format(message)
