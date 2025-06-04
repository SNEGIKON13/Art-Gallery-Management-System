from typing import Sequence, Optional
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.interfaces.exhibition_service import IExhibitionService

class ListExhibitionsCommand(BaseCommand):
    def __init__(self, exhibition_service: IExhibitionService, user_service):
        super().__init__(user_service)
        self._exhibition_service = exhibition_service

    def execute(self, args: Sequence[str]) -> Optional[str]:
        exhibitions = self._exhibition_service.get_all_exhibitions()
        if not exhibitions:
            return "No exhibitions found"
        
        output_lines = []
        separator = "-" * 60  # Consistent separator length
        output_lines.append(f"Total exhibitions: {len(exhibitions)}")
        output_lines.append(separator)

        # Sort by ID for easier viewing if IDs are not sequential or guaranteed sorted
        # exhibitions.sort(key=lambda ex: ex.id) # Uncomment if sorting is needed

        for exhibition in exhibitions:
            output_lines.append(f"ID: {exhibition.id}")
            output_lines.append(f"Title: {exhibition.title}")
            output_lines.append(f"Start date: {exhibition.start_date}")
            output_lines.append(f"End date: {exhibition.end_date}")
            if exhibition != exhibitions[-1]: # Add separator for all but the last exhibition
                output_lines.append(separator)
        
        return "\n".join(output_lines)

    def get_name(self) -> str:
        return "list_exhibitions"

    def get_description(self) -> str:
        return "List all exhibitions"

    def get_usage(self) -> str:
        return "list_exhibitions"
        
    def get_help(self) -> str:
        return ("Shows a list of all exhibitions in the gallery.\n"
                "Displays basic information about each exhibition including:\n"
                "  - Exhibition ID\n"
                "  - Title\n"
                "  - Start and end dates\n"
                "Use 'get_exhibition <id>' for more detailed information.")
