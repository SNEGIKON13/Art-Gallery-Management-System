from datetime import datetime
from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.services.exhibition_service import IExhibitionService
from art_gallery.ui.exceptions.validation_exceptions import MissingRequiredArgumentError, InvalidInputError
from art_gallery.ui.decorators import admin_only, authenticated, transaction, log_command

class CreateExhibitionCommand(BaseCommand):
    def __init__(self, exhibition_service: IExhibitionService, user_service):
        super().__init__(user_service)
        self._exhibition_service = exhibition_service

    @admin_only
    @authenticated
    @transaction
    @log_command
    def execute(self, args: Sequence[str]) -> None:
        if len(args) != 5:
            raise MissingRequiredArgumentError(
                "Required: title, description, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), max_capacity"
            )
        
        title, description, start_date_str, end_date_str, max_capacity_str = args
        
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            max_capacity = int(max_capacity_str) if max_capacity_str != "None" else None
            
            if start_date > end_date:
                raise InvalidInputError("End date must be after start date")
            
            exhibition = self._exhibition_service.create_exhibition(
                title, description, start_date, end_date, max_capacity
            )
            print(f"Exhibition created successfully with ID: {exhibition.id}")
        except ValueError as e:
            raise InvalidInputError(f"Invalid date format or capacity: {str(e)}")

    def get_name(self) -> str:
        return "create_exhibition"

    def get_description(self) -> str:
        return "Create a new exhibition"

    def get_usage(self) -> str:
        return "create_exhibition <title> <description> <start_date> <end_date> <max_capacity>"
        
    def get_help(self) -> str:
        return ("Creates a new exhibition in the gallery.\n"
                "Only administrators can use this command.\n"
                "Parameters:\n"
                "  - title: Name of the exhibition\n"
                "  - description: Detailed description\n"
                "  - start_date: Start date (YYYY-MM-DD)\n"
                "  - end_date: End date (YYYY-MM-DD)\n"
                "  - max_capacity: Maximum number of visitors (or None)\n"
                "Example: create_exhibition 'Modern Art' 'Contemporary pieces' 2024-01-01 2024-02-01 100")
