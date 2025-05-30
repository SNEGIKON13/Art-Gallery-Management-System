from functools import wraps
from typing import Callable, Any
from exceptions.auth_exceptions import UnauthorizedError, PermissionDeniedError

def admin_only(command_func: Callable) -> Callable:
    @wraps(command_func)
    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        if not self._current_user:
            raise UnauthorizedError("No user logged in")
        if not self._current_user.is_admin():
            raise PermissionDeniedError("This command requires administrator privileges")
        return command_func(self, *args, **kwargs)
    return wrapper
