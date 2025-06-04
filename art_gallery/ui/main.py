import argparse
import os
import logging # Добавляем стандартный logging
import json
from typing import Optional, Dict, Any
from art_gallery.infrastructure.config.cli_config import CLIConfig
from art_gallery.infrastructure.logging.implementations.file_logger import FileLogger
from art_gallery.infrastructure.logging.implementations.composite_logger import CompositeLogger
from art_gallery.infrastructure.logging.implementations.filtered_logger import FilteredLogger
from art_gallery.ui.handlers.error_handler import ConsoleErrorHandler
from art_gallery.ui.command_registry.command_registry import CommandRegistry
from art_gallery.ui.command_registry.command_parser import CommandParser
from art_gallery.ui.services import create_real_services, create_mock_services  
from art_gallery.infrastructure.config import ConfigRegistry, SerializationConfig
from art_gallery.infrastructure.config.config_manager import ConfigManager
from art_gallery.infrastructure.logging.interfaces.logger import LogLevel
from art_gallery.ui.command_registry.command_registrar import register_commands

# Настройка базового логирования для вывода DEBUG сообщений в консоль
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler() # Вывод в консоль (stderr по умолчанию)
    ]
)

class Application:
    def __init__(self, args: Optional[argparse.Namespace] = None):
        # Инициализация конфигурации
        self.config = CLIConfig()
        self.config_manager = ConfigManager()
        self.config_registry = ConfigRegistry()
        
        # Парсинг аргументов командной строки, если не переданы
        if args is None:
            parser = argparse.ArgumentParser(description='Art Gallery Management System')
            parser.add_argument('--format', type=str, choices=['json', 'xml'], default=None,
                                help='Формат данных для использования (json или xml)')
            parser.add_argument('--test', action='store_true', help='Использовать тестовые сервисы')
            args = parser.parse_args()
            
        # Определение формата данных с приоритетом:
        # 1. Аргументы командной строки
        # 2. ConfigRegistry (.env файл)
        # 3. Старый ConfigManager (обратная совместимость)
        if args.format:
            format_name = args.format
        else:
            try:
                # Попытаться загрузить из нового ConfigRegistry
                format_name = self.config_registry.get_serialization_config().format
            except Exception:
                # Если не получилось, использовать старый ConfigManager
                format_name = self.config_manager.get("format", "json")
        
        # Сохранение формата в обе системы конфигурации, если он задан через аргументы
        if args.format:
            # Обновляем старый ConfigManager для совместимости
            self.config_manager.set("format", args.format)
            self.config_manager.save()
            
            # Обновляем .env файл для ConfigRegistry
            try:
                self._update_env_file("SERIALIZATION_FORMAT", args.format)
            except Exception:
                pass  # Игнорируем ошибки при обновлении .env
            
        # Инициализация логгеров
        app_logger = FilteredLogger(
            FileLogger("logs/app.log"), 
            {LogLevel.INFO, LogLevel.DEBUG}
        )
        error_logger = FilteredLogger(
            FileLogger("logs/errors.log"), 
            {LogLevel.ERROR, LogLevel.CRITICAL, LogLevel.WARNING}
        )
        
        self.logger = CompositeLogger([app_logger, error_logger])
        self.error_handler = ConsoleErrorHandler(self.logger)
        
        # Вывод информации о выбранном формате
        print(f"Используем формат данных: {format_name.upper()}")
        
        # Инициализация сервисов
        if args.test:
            self.services = create_mock_services()
        else:
            self.services = create_real_services(format_name=format_name)
            
        # Инициализация команд
        self.command_parser = CommandParser()
        self.command_registry = CommandRegistry(self.command_parser)
        
        # Регистрация команд
        register_commands(self.command_registry, self.services, self.logger)

    def _update_env_file(self, key: str, value: str) -> None:
        """Обновляет значение в файле .env"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        env_path = os.path.join(base_dir, '.env')
        
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            updated = False
            for i, line in enumerate(lines):
                if line.startswith(f"{key}=") or line.startswith(f"{key} ="):
                    lines[i] = f"{key}={value}\n"
                    updated = True
                    break
            
            if not updated:
                if lines and not lines[-1].endswith('\n'):
                    lines[-1] += '\n'
                lines.append(f"{key}={value}\n")
            
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
    
    def run(self) -> None:
        self.logger.info("Application started")
        print(self.config.format_message("Welcome to Art Gallery Management System", "info"))
        
        while True:
            try:
                command = input(self.config.prompt_symbol).strip()
                if command.lower() == "exit":
                    print(self.config.format_message("Goodbye!", "info"))
                    break
                
                # Выполняем команду
                result = self.command_registry.execute(command)
                if result:
                    print(self.config.format_message(result, "success"))
                
            except KeyboardInterrupt:
                self.logger.info("Application terminated by user")
                print(self.config.format_message("\nExiting...", "info"))
                break
            except Exception as e:
                self.error_handler.handle_error(e)

        self.logger.info("Application stopped")

def main() -> None:
    # Создание и запуск приложения
    app = Application()
    app.run()

if __name__ == "__main__":
    main()
