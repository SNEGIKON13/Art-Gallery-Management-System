import os
from datetime import datetime
from typing import Any, TextIO
from art_gallery.infrastructure.logging.interfaces.logger import ILogger, LogLevel

class FileLogger(ILogger):
    def __init__(self, log_file_path: str):
        self._log_file_path = log_file_path
        self._ensure_log_directory_exists()
        self._file: TextIO = open(log_file_path, 'a', encoding='utf-8')

    def _ensure_log_directory_exists(self) -> None:
        """Ensure the directory for the log file exists"""
        os.makedirs(os.path.dirname(self._log_file_path), exist_ok=True)

    def _format_message(self, level: LogLevel, message: str, **kwargs: Any) -> str:
        """Format log message with timestamp and additional data"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] [{level.value}] {message}"
        
        if kwargs:
            extra_data = " ".join(f"{k}={v}" for k, v in kwargs.items())
            formatted_message += f" | {extra_data}"
            
        return formatted_message + "\n"

    def debug(self, message: str, **kwargs: Any) -> None:
        self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self.log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self.log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self.log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        self.log(LogLevel.CRITICAL, message, **kwargs)

    def log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        formatted_message = self._format_message(level, message, **kwargs)
        self._file.write(formatted_message)
        self._file.flush()

    def __del__(self) -> None:
        """Ensure file is closed when object is destroyed"""
        if hasattr(self, '_file'):
            self._file.close()
