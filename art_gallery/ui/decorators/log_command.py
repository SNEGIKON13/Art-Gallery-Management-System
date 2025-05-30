from functools import wraps
from typing import Callable, Any
from datetime import datetime
from art_gallery.infrastructure.logging.interfaces.logger import LogLevel

def log_command(logger):
    def decorator(command_func: Callable) -> Callable:
        @wraps(command_func)
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            command_name = self.get_name()
            user_id = self._current_user.id if self._current_user else "anonymous"
            start_time = datetime.now()
            
            try:
                result = command_func(self, *args, **kwargs)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                logger.info(
                    "Command executed",
                    command=command_name,
                    user=user_id,
                    duration=f"{duration:.3f}s",
                    args=args,
                    success=True
                )
                return result
            except Exception as e:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                logger.error(
                    "Command failed",
                    command=command_name,
                    user=user_id,
                    duration=f"{duration:.3f}s",
                    args=args,
                    error=str(e)
                )
                raise
        return wrapper
    return decorator
