from .base_exception import UIException

class ValidationException(UIException):
    """Базовое исключение для ошибок валидации"""
    pass

class InvalidInputError(ValidationException):
    """Некорректные входные данные"""
    pass

class MissingRequiredArgumentError(ValidationException):
    """Отсутствует обязательный аргумент"""
    pass

class InvalidArgumentTypeError(ValidationException):
    """Неверный тип аргумента"""
    pass
