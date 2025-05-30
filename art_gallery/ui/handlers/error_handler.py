import logging
from datetime import datetime
from typing import Dict, Type
from art_gallery.ui.interfaces.error_handler import IErrorHandler
from art_gallery.ui.exceptions.base_exception import UIException
from art_gallery.ui.exceptions.command_exceptions import CommandException, CommandNotFoundError
from art_gallery.ui.exceptions.validation_exceptions import ValidationException
from art_gallery.ui.exceptions.auth_exceptions import AuthException
from art_gallery.ui.exceptions.business_exceptions import BusinessException
from art_gallery.infrastructure.logging.interfaces.logger import ILogger

class ConsoleErrorHandler(IErrorHandler):
    def __init__(self, logger: ILogger):
        self._logger = logger
        self._error_formatters = self._setup_formatters()

    def _setup_formatters(self) -> Dict[Type[UIException], str]:
        return {
            CommandNotFoundError: "Неизвестная команда. Используйте 'help' для списка команд",
            CommandException: "Ошибка команды: {message}",
            ValidationException: "Ошибка валидации: {message}",
            AuthException: "Ошибка доступа: {message}",
            BusinessException: "Ошибка: {message}"
        }

    def handle_error(self, error: Exception) -> None:
        """Обработать ошибку, вывести сообщение и записать в лог"""
        formatted_message = self.format_error(error)
        print(f"\033[91m{formatted_message}\033[0m")  # Красный цвет для ошибок
        self.log_error(error)

    def format_error(self, error: Exception) -> str:
        """Форматировать ошибку в читаемое сообщение"""
        if not isinstance(error, UIException):
            return f"Внутренняя ошибка: {str(error)}"

        for error_type, template in self._error_formatters.items():
            if isinstance(error, error_type):
                return template.format(message=error.message)
        
        return str(error)

    def log_error(self, error: Exception) -> None:
        """Записать ошибку в лог"""
        error_type = type(error).__name__
        self._logger.error(
            "Application error occurred",
            error_type=error_type,
            error_message=str(error)
        )
