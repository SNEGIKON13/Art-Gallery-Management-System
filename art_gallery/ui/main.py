import argparse
import os
import json
from typing import Optional, Dict, Any
from art_gallery.infrastructure.config.cli_config import CLIConfig
from art_gallery.infrastructure.logging.implementations.file_logger import FileLogger
from art_gallery.infrastructure.logging.implementations.composite_logger import CompositeLogger
from art_gallery.infrastructure.logging.implementations.filtered_logger import FilteredLogger
from art_gallery.ui.handlers.error_handler import ConsoleErrorHandler
from art_gallery.ui.command_registry import CommandRegistry
from art_gallery.ui.command_parser import CommandParser
from art_gallery.ui.command_registrar import register_commands
from art_gallery.ui.services import create_real_services, create_mock_services
from art_gallery.infrastructure.config.config_manager import ConfigManager
from art_gallery.infrastructure.logging.interfaces.logger import LogLevel

class Application:
    def __init__(self, args: Optional[argparse.Namespace] = None):
        # Инициализация конфигурации
        self.config = CLIConfig()
        self.config_manager = ConfigManager()
        
        # Парсинг аргументов командной строки, если не переданы
        if args is None:
            parser = argparse.ArgumentParser(description='Art Gallery Management System')
            parser.add_argument('--format', type=str, choices=['json', 'xml'], default=None,
                                help='Формат данных для использования (json или xml)')
            parser.add_argument('--test', action='store_true', help='Использовать тестовые сервисы')
            args = parser.parse_args()
            
        # Определение формата данных: сначала из аргументов, если нет - из конфигурации
        format_name = args.format or self.config_manager.get("format", "json")
        
        # Сохранение формата в конфигурацию, если он задан через аргументы
        if args.format and args.format != self.config_manager.get("format", None):
            self.config_manager.set("format", args.format)
            self.config_manager.save()
            
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
