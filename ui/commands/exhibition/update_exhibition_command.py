from datetime import datetime
from typing import Sequence
from ...commands.base_command import BaseCommand
from application.services.exhibition_service import IExhibitionService
from ...exceptions.command_exceptions import InvalidArgumentsException

class UpdateExhibitionCommand(BaseCommand):
    def __init__(self, exhibition_service: IExhibitionService, user_service):
        super().__init__(user_service)
        self._exhibition_service = exhibition_service

    def execute(self, args: Sequence[str]) -> None:
        if len(args) != 6:
            raise InvalidArgumentsException(
                "Required: exhibition_id title description start_date end_date max_capacity"
            )
        
        exhibition_id_str, title, description, start_date_str, end_date_str, max_capacity_str = args
        
        try:
            exhibition_id = int(exhibition_id_str)
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str != "None" else None
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str != "None" else None
            max_capacity = int(max_capacity_str) if max_capacity_str != "None" else None
            
            title = None if title == "None" else title
            description = None if description == "None" else description
            
            exhibition = self._exhibition_service.update_exhibition(
                exhibition_id, title, description, start_date, end_date, max_capacity
            )
            print(f"Exhibition {exhibition_id} updated successfully")
        except ValueError as e:
            raise InvalidArgumentsException(str(e))

    def get_name(self) -> str:
        return "update_exhibition"

    def get_description(self) -> str:
        return "Update an exhibition"

    def get_usage(self) -> str:
        return "update_exhibition <exhibition_id> <title> <description> <start_date> <end_date> <max_capacity>"
