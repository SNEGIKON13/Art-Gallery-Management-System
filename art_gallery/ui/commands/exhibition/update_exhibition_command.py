from typing import Sequence
from datetime import datetime
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.interfaces.exhibition_service import IExhibitionService
from art_gallery.exceptions.validation_exceptions import MissingRequiredArgumentError, InvalidInputError
from art_gallery.exceptions.command_exceptions import CommandExecutionError
from art_gallery.ui.decorators import admin_only, authenticated, log_command

class UpdateExhibitionCommand(BaseCommand):
    def __init__(self, exhibition_service: IExhibitionService, user_service):
        super().__init__(user_service)
        self._exhibition_service = exhibition_service

    @admin_only
    @authenticated
    @log_command
    def execute(self, args: Sequence[str]) -> None:
        if len(args) != 6:
            raise MissingRequiredArgumentError(
                "Required: exhibition_id, title, description, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), max_capacity"
            )
        
        exhibition_id_str, title, description, start_date_str, end_date_str, max_capacity_str = args
        
        try:
            exhibition_id = int(exhibition_id_str)
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            max_capacity = int(max_capacity_str) if max_capacity_str != "None" else None

            if start_date > end_date:
                raise InvalidInputError("End date must be after start date")

            self._exhibition_service.update_exhibition(
                exhibition_id, title, description, start_date, end_date, max_capacity
            )
            print(f"Exhibition {exhibition_id} updated successfully")
        except ValueError as e:
            raise InvalidInputError(f"Invalid date format, ID or capacity: {str(e)}")
        except Exception as e:
            raise CommandExecutionError(f"Failed to update exhibition: {str(e)}")

    def get_name(self) -> str:
        return "update_exhibition"

    def get_description(self) -> str:
        return "Update exhibition details"

    def get_usage(self) -> str:
        return "update_exhibition <exhibition_id> <title> <description> <start_date> <end_date> <max_capacity>"
        
    def get_help(self) -> str:
        return ("Updates an existing exhibition's details.\n"
                "Only administrators can use this command.\n"
                "Parameters:\n"
                "  - exhibition_id: The unique identifier of the exhibition\n"
                "  - title: New name of the exhibition\n"
                "  - description: New description\n"
                "  - start_date: New start date (YYYY-MM-DD)\n"
                "  - end_date: New end date (YYYY-MM-DD)\n"
                "  - max_capacity: New maximum capacity (or None)\n"
                "Example: update_exhibition 1 'Modern Art 2024' 'Updated show' 2024-02-01 2024-03-01 150")
