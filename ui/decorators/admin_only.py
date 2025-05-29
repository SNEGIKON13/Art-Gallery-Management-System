from functools import wraps
from typing import Callable, Any
from ..exceptions.command_exceptions import AuthorizationException

def admin_only(command_func: Callable) -> Callable:
    @wraps(command_func)
    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        if not self._current_user:
            raise AuthorizationException("No user logged in")
        if not self._current_user.is_admin():
            raise AuthorizationException("This command requires administrator privileges")
        return command_func(self, *args, **kwargs)
    return wrapper
