from art_gallery.repository.implementations.unit_of_work import UnitOfWork

class BaseService:
    def __init__(self, unit_of_work: UnitOfWork):
        self._uow = unit_of_work

    def _execute_in_transaction(self, action):
        """Выполняет действие в транзакции"""
        try:
            with self._uow:
                result = action()
            return result
        except Exception as e:
            # Можно добавить логирование
            raise
