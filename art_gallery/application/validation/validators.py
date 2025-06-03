from datetime import datetime
from typing import List
from art_gallery.domain import User, Exhibition, UserRole

class BusinessRuleValidator:
    @staticmethod
    def validate_admin_access(user: User) -> None:
        """Проверяет права администратора"""
        if not user or user.role != UserRole.ADMIN:
            raise ValueError("Access denied: admin rights required")

    @staticmethod
    def validate_exhibition_dates(start_date: datetime, end_date: datetime) -> None:
        """Проверяет даты выставки"""
        now = datetime.now()
        if start_date < now:
            raise ValueError("Exhibition cannot start in the past")
        if end_date < now:
            raise ValueError("Exhibition cannot end in the past")
        if (end_date - start_date).days > 365:
            raise ValueError("Exhibition cannot last more than a year")

    @staticmethod
    def validate_exhibition_capacity(exhibition: Exhibition, artwork_ids: List[int]) -> None:
        """Проверяет количество экспонатов"""
        if len(artwork_ids) < 1:
            raise ValueError("Exhibition must have at least one artwork")
        if exhibition.max_capacity and len(artwork_ids) > exhibition.max_capacity:
            raise ValueError(f"Exhibition cannot have more than {exhibition.max_capacity} artworks")
