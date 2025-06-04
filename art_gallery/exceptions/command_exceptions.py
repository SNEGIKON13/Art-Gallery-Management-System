from art_gallery.exceptions.base_exception import UIException

class CommandException(UIException):
    """Базовое исключение для ошибок команд"""
    pass

class CommandNotFoundError(CommandException):
    """Команда не найдена"""
    pass

class InvalidCommandFormatError(CommandException):
    """Неверный формат команды"""
    pass

class CommandExecutionError(CommandException):
    """Ошибка выполнения команды"""
    pass
