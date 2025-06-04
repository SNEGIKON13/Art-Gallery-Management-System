from datetime import datetime
from domain import Exhibition
from .base_specification import Specification

class ActiveExhibitionSpecification(Specification[Exhibition]):
    def is_satisfied_by(self, item: Exhibition) -> bool:
        return item.is_active()

class ExhibitionByDateRangeSpecification(Specification[Exhibition]):
    def __init__(self, start_date: datetime, end_date: datetime):
        self.start_date = start_date
        self.end_date = end_date

    def is_satisfied_by(self, item: Exhibition) -> bool:
        return item.start_date <= self.end_date and item.end_date >= self.start_date

class HasArtworkSpecification(Specification[Exhibition]):
    def __init__(self, artwork_id: int):
        self.artwork_id = artwork_id

    def is_satisfied_by(self, item: Exhibition) -> bool:
        return self.artwork_id in item.artwork_ids
