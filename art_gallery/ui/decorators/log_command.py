from functools import wraps
from typing import Callable, Any
import logging
from datetime import datetime

def log_command(command_func: Callable) -> Callable:
    @wraps(command_func)
    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        command_name = self.get_name()
        user_id = self._current_user.id if self._current_user else "anonymous"
        start_time = datetime.now()
        
        try:
            result = command_func(self, *args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logging.info(
                f"Command executed: {command_name} | "
                f"User: {user_id} | "
                f"Duration: {duration}s | "
                f"Args: {args} | "
                f"Success: True"
            )
            return result
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logging.error(
                f"Command failed: {command_name} | "
                f"User: {user_id} | "
                f"Duration: {duration}s | "
                f"Args: {args} | "
                f"Error: {str(e)}"
            )
            raise
    return wrapper
