from typing import List, Any
from art_gallery.infrastructure.logging.interfaces.logger import ILogger, LogLevel

class CompositeLogger(ILogger):
    def __init__(self, loggers: List[ILogger]):
        self._loggers = loggers

    def debug(self, message: str, **kwargs: Any) -> None:
        for logger in self._loggers:
            logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        for logger in self._loggers:
            logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        for logger in self._loggers:
            logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        for logger in self._loggers:
            logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        for logger in self._loggers:
            logger.critical(message, **kwargs)

    def log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        for logger in self._loggers:
            logger.log(level, message, **kwargs)
