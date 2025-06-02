from dataclasses import dataclass, field
from typing import Dict
import os

@dataclass
class CLIConfig:
    # Символ приглашения к вводу
    prompt_symbol: str = "> "
    
    # ANSI коды цветов
    colors: Dict[str, str] = field(default_factory=dict)
    
    # Формат сообщений
    message_format: Dict[str, str] = field(default_factory=dict)
      # Настройки сериализации
    serialization_config: Dict[str, str] = field(default_factory=lambda: {
        'default_format': 'json',  # Формат по умолчанию (json/xml)    # Директория для экспорта
    })
    
    def __post_init__(self) -> None:
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

        # Создаем директорию для экспорта если её нет
        export_dir = os.path.join(project_root, self.serialization_config['export_dir'])
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            
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
