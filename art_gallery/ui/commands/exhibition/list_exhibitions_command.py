from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.services.exhibition_service import IExhibitionService

class ListExhibitionsCommand(BaseCommand):
    def __init__(self, exhibition_service: IExhibitionService, user_service):
        super().__init__(user_service)
        self._exhibition_service = exhibition_service

    def execute(self, args: Sequence[str]) -> None:
        exhibitions = self._exhibition_service.get_all_exhibitions()
        if not exhibitions:
            print("No exhibitions found")
            return
            
        for exhibition in exhibitions:
            print(f"ID: {exhibition.id}")
            print(f"Title: {exhibition.title}")
            print(f"Start date: {exhibition.start_date}")
            print(f"End date: {exhibition.end_date}")
            print("-" * 30)

    def get_name(self) -> str:
        return "list_exhibitions"

    def get_description(self) -> str:
        return "List all exhibitions"

    def get_usage(self) -> str:
        return "list_exhibitions"
