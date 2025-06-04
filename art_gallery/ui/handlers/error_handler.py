import logging
from datetime import datetime
from typing import Dict, Type
from art_gallery.ui.interfaces.error_handler import IErrorHandler
from art_gallery.exceptions.base_exception import UIException
from art_gallery.exceptions.command_exceptions import CommandException, CommandNotFoundError
from art_gallery.exceptions.validation_exceptions import ValidationException
from art_gallery.exceptions.auth_exceptions import AuthException
from art_gallery.exceptions.business_exceptions import BusinessException
from art_gallery.infrastructure.logging.interfaces.logger import ILogger
from art_gallery.infrastructure.config.cli_config import CLIConfig # Добавляем импорт

class ConsoleErrorHandler(IErrorHandler):
    def __init__(self, logger: ILogger, cli_config: CLIConfig): # Добавляем cli_config
        self._logger = logger
        self.config = cli_config # Сохраняем cli_config
        self._error_formatters = self._setup_formatters()

    def _setup_formatters(self) -> Dict[Type[UIException], str]:
        return {
            CommandNotFoundError: "Unknown command. Use 'help' for a list of commands.",
            CommandException: "Command error: {message}",
            ValidationException: "Validation error: {message}",
            AuthException: "Access error: {message}",
            BusinessException: "Error: {message}"
        }

    def handle_error(self, error: Exception) -> None:
        """Обработать ошибку, вывести сообщение и записать в лог"""
        formatted_message = self.format_error(error)
        print(self.config.format_message(formatted_message, "error"))
        self.log_error(error)

    def format_error(self, error: Exception) -> str:
        """Форматировать ошибку в читаемое сообщение"""
        if not isinstance(error, UIException):
            return f"Internal error: {str(error)}"

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
