from dataclasses import dataclass, field
from typing import Dict

@dataclass
class CLIConfig:
    # Символ приглашения к вводу
    prompt_symbol: str = "> "
    
    # ANSI коды цветов
    colors: Dict[str, str] = field(default_factory=dict)
    
    # Формат сообщений
    message_format: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
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
