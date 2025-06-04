from art_gallery.exceptions.base_exception import UIException

class AuthException(UIException):
    """Базовое исключение для ошибок авторизации"""
    pass

class UnauthorizedError(AuthException):
    """Пользователь не авторизован"""
    pass

class PermissionDeniedError(AuthException):
    """Отказано в доступе"""
    pass

class AuthenticationError(AuthException):
    """Ошибка аутентификации"""
    pass
