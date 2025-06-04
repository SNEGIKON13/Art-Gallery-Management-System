import argparse
import os
import logging # Добавляем стандартный logging
logging.disable(logging.CRITICAL + 1) # ПОЛНОСТЬЮ ОТКЛЮЧАЕМ СТАНДАРТНЫЙ ЛОГГИНГ
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
from art_gallery.infrastructure.logging.interfaces.logger import LogLevel
from art_gallery.ui.command_registry.command_registrar import register_commands

# Настройка базового логирования БЫЛА ЗДЕСЬ (теперь отключено через logging.disable)

class Application:
    def __init__(self, args: Optional[argparse.Namespace] = None):
        # Инициализация конфигурации
        self.config = CLIConfig()
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
        if args.format:
            format_name = args.format
        else:
            try:
                # Загружаем из ConfigRegistry (.env файл)
                format_name = self.config_registry.get_serialization_config().format
            except Exception as e:
                logging.warning(f"Ошибка при чтении формата из ConfigRegistry: {e}")
                # Используем значение по умолчанию
                format_name = "json"
        
        # Сохранение формата в .env файл, если он задан через аргументы
        if args.format:
            # Обновляем .env файл через ConfigRegistry
            try:
                ConfigRegistry.update_env_variable("SERIALIZATION_FORMAT", args.format)
            except Exception as e:
                logging.warning(f"Не удалось обновить переменную SERIALIZATION_FORMAT в .env: {e}")
            
        # Инициализация логгеров
        app_logger = FilteredLogger(
            FileLogger("logs/app.log"), 
            {LogLevel.INFO, LogLevel.DEBUG}
        )
        error_logger = FilteredLogger(
            FileLogger("logs/errors.log"), 
            {LogLevel.ERROR, LogLevel.CRITICAL, LogLevel.WARNING}
        )
        
        # Инициализация логгеров (ПОДАВЛЕНО)
        # app_logger = FilteredLogger(
        #     FileLogger("logs/app.log"), 
        #     {LogLevel.INFO, LogLevel.DEBUG}
        # )
        # error_logger = FilteredLogger(
        #     FileLogger("logs/errors.log"), 
        #     {LogLevel.ERROR, LogLevel.CRITICAL, LogLevel.WARNING}
        # )
        
        self.logger = CompositeLogger([]) # ПОДАВЛЯЕМ ВСЕ КАСТОМНЫЕ ЛОГИ
        self.error_handler = ConsoleErrorHandler(self.logger, self.config) # Передаем self.config
        
        # Вывод информации о выбранном формате (ПОДАВЛЕНО, как техническая информация)
        # print(f"Используем формат данных: {format_name.upper()}")
        
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

    # Метод _update_env_file удален, так как теперь используется ConfigRegistry.update_env_variable
    
    def run(self) -> None:
        self.logger.info("Application started") # Этот лог уже подавлен через CompositeLogger([])
        print(self.config.format_message("Welcome to Art Gallery Management System", "info"))
        
        while True:
            try:
                prompt_colored = f"{self.config.colors.get('prompt', '')}{self.config.prompt_symbol}{self.config.colors.get('reset', '')}"
                command = input(prompt_colored).strip()
                if command.lower() == "exit":
                    print(self.config.format_message("Goodbye!", "info"))
                    break
                
                # Выполняем команду
                result = self.command_registry.execute(command)
                if result:
                    print(self.config.format_message(result, "info")) # Изменено на info для общего случая
                
            except KeyboardInterrupt:
                self.logger.info("Application terminated by user") # Этот лог уже подавлен
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
