class CommandException(Exception):
    """Базовое исключение для команд"""
    pass

class InvalidArgumentsException(CommandException):
    """Неверные аргументы команды"""
    pass

class AuthenticationException(CommandException):
    """Ошибка аутентификации"""
    pass

class AuthorizationException(CommandException):
    """Ошибка авторизации"""
    pass
