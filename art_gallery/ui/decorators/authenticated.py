from functools import wraps
from typing import Callable, Any
from art_gallery.exceptions.auth_exceptions import AuthException

def authenticated(command_func: Callable) -> Callable:
    @wraps(command_func)
    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        if not self._current_user:
            raise AuthException("You must be logged in to use this command")
        if not self._current_user.can_login():
            raise AuthException("Your account is deactivated")
        return command_func(self, *args, **kwargs)
    return wrapper
