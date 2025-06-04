from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.exceptions.auth_exceptions import PermissionDeniedError
from art_gallery.domain import UserRole

class ListUsersCommand(BaseCommand):
    def __init__(self, user_service):
        super().__init__(user_service)
        
    def execute(self, args: Sequence[str]) -> None:
        # Check administrator rights
        if not self._current_user or self._current_user.role != UserRole.ADMIN:
            raise PermissionDeniedError("This command is available to administrators only")
            
        users = self._user_service.get_all_users()
        
        if not users:
            print("There are no users in the system.")
            return
            
        print(f"Total users: {len(users)}")
        print("-" * 80)
        
        # Sort by ID for easier viewing
        sorted_users = sorted(users, key=lambda u: u.id)
        
        for user in sorted_users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Role: {user.role.name}")
            print(f"Active: {'Yes' if user.is_active else 'No'}")
            print(f"Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if user.last_login:
                print(f"Last login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 50)
            
    def get_name(self) -> str:
        return "list_users"
        
    def get_description(self) -> str:
        return "Show a list of all users (admin only)"
        
    def get_usage(self) -> str:
        return "list_users"
        
    def get_help(self) -> str:
        return ("Displays a list of all users in the system.\n"
                "For each user, shows ID, username, role, status, and dates.\n"
                "This command is available to administrators only.")
