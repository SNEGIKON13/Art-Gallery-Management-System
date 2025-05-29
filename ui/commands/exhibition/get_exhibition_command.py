from typing import Sequence
from ...commands.base_command import BaseCommand
from application.services.exhibition_service import IExhibitionService
from ...exceptions.command_exceptions import InvalidArgumentsException

class GetExhibitionCommand(BaseCommand):
    def __init__(self, exhibition_service: IExhibitionService, user_service):
        super().__init__(user_service)
        self._exhibition_service = exhibition_service

    def execute(self, args: Sequence[str]) -> None:
        if len(args) != 1:
            raise InvalidArgumentsException("Required: exhibition_id")
        
        try:
            exhibition_id = int(args[0])
            exhibition = self._exhibition_service.get_exhibition(exhibition_id)
            if exhibition:
                print(f"ID: {exhibition.id}")
                print(f"Title: {exhibition.title}")
                print(f"Description: {exhibition.description}")
                print(f"Start date: {exhibition.start_date}")
                print(f"End date: {exhibition.end_date}")
                print(f"Max capacity: {exhibition.max_capacity}")
                print(f"Artwork IDs: {exhibition.artwork_ids}")
            else:
                print(f"Exhibition {exhibition_id} not found")
        except ValueError as e:
            raise InvalidArgumentsException(str(e))

    def get_name(self) -> str:
        return "get_exhibition"

    def get_description(self) -> str:
        return "Get exhibition details"

    def get_usage(self) -> str:
        return "get_exhibition <exhibition_id>"
