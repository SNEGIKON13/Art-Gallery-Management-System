from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.exceptions.auth_exceptions import PermissionDeniedError
from art_gallery.ui.exceptions.validation_exceptions import ValidationError
from art_gallery.domain import UserRole

class GetUserCommand(BaseCommand):
    def __init__(self, user_service):
        super().__init__(user_service)
        
    def execute(self, args: Sequence[str]) -> None:
        # Check administrator rights
        if not self._current_user or self._current_user.role != UserRole.ADMIN:
            raise PermissionDeniedError("This command is available to administrators only")
            
        if not args:
            raise ValidationError("You must specify a user ID or the --username parameter")
            
        user = None
        
        if args[0] == "--username":
            if len(args) < 2:
                raise ValidationError("You must provide a username after --username")
                
            username = args[1]
            user = self._user_service.get_user_by_username(username)
            if not user:
                print(f"User with username '{username}' not found")
                return
        else:
            try:
                user_id = int(args[0])
                user = self._user_service.get_user_by_id(user_id)
                if not user:
                    print(f"User with ID {user_id} not found")
                    return
            except ValueError:
                raise ValidationError("User ID must be an integer")
        
        # Display user information
        print(f"User information:")
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Role: {user.role.name}")
        print(f"Active: {'Yes' if user.is_active else 'No'}")
        print(f"Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if user.last_login:
            print(f"Last login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S')}")
            
    def get_name(self) -> str:
        return "get_user"
        
    def get_description(self) -> str:
        return "Get user information (admin only)"
        
    def get_usage(self) -> str:
        return "get_user <user_id> | get_user --username <username>"
        
    def get_help(self) -> str:
        return ("Displays detailed information about a user.\n"
                "Usage options:\n"
                "1. get_user <id> - Search user by ID\n"
                "2. get_user --username <username> - Search user by username\n"
                "This command is available to administrators only.")
