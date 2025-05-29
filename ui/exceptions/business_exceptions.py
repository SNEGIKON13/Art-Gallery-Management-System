from .base_exception import UIException

class BusinessException(UIException):
    """Базовое исключение для бизнес-ошибок"""
    pass

class EntityNotFoundError(BusinessException):
    """Сущность не найдена"""
    pass

class DuplicateEntityError(BusinessException):
    """Сущность уже существует"""
    pass

class InvalidOperationError(BusinessException):
    """Недопустимая операция"""
    pass
