from functools import wraps
from typing import Callable, Any
from ..exceptions.command_exceptions import AuthenticationException

def authenticated(command_func: Callable) -> Callable:
    @wraps(command_func)
    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        if not self._current_user:
            raise AuthenticationException("You must be logged in to use this command")
        if not self._current_user.can_login():
            raise AuthenticationException("Your account is deactivated")
        return command_func(self, *args, **kwargs)
    return wrapper
