from typing import Any, Set
from art_gallery.infrastructure.logging.interfaces.logger import ILogger, LogLevel

class FilteredLogger(ILogger):
    def __init__(self, logger: ILogger, allowed_levels: Set[LogLevel]):
        self._logger = logger
        self._allowed_levels = allowed_levels

    def _should_log(self, level: LogLevel) -> bool:
        return level in self._allowed_levels

    def debug(self, message: str, **kwargs: Any) -> None:
        if self._should_log(LogLevel.DEBUG):
            self._logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        if self._should_log(LogLevel.INFO):
            self._logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        if self._should_log(LogLevel.WARNING):
            self._logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        if self._should_log(LogLevel.ERROR):
            self._logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        if self._should_log(LogLevel.CRITICAL):
            self._logger.critical(message, **kwargs)

    def log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        if self._should_log(level):
            self._logger.log(level, message, **kwargs)
