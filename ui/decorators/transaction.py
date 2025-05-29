from functools import wraps
from typing import Callable, Any
import logging

def transaction(command_func: Callable) -> Callable:
    @wraps(command_func)
    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        try:
            result = command_func(self, *args, **kwargs)
            # Здесь будет коммит транзакции, когда добавим поддержку транзакций
            return result
        except Exception as e:
            # Здесь будет откат транзакции
            logging.error(f"Transaction failed: {str(e)}")
            raise
    return wrapper
