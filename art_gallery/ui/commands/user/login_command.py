from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.exceptions.validation_exceptions import MissingRequiredArgumentError
from art_gallery.exceptions.auth_exceptions import AuthenticationError

class LoginCommand(BaseCommand):
    def __init__(self, user_service, command_registry):
        super().__init__(user_service)
        self._registry = command_registry

    def get_name(self) -> str:
        return "login"

    def get_description(self) -> str:
        return "Login to the system"

    def get_usage(self) -> str:
        return "login <username> <password>"

    def get_help(self) -> str:
        return ("Authenticates a user in the system.\n"
                "The command requires both username and password.\n"
                "After successful login, you will have access to user-specific commands.\n"
                "Usage: login <username> <password>")

    def execute(self, args: Sequence[str]) -> None:
        if len(args) != 2:
            raise MissingRequiredArgumentError("Username and password required")
        
        current_user_in_registry = self._registry.get_current_user()
        if current_user_in_registry:
            # This block should be entered if a user is already logged in.
            # The bug you observed means this condition is currently not met
            # when the second user logs in.
            
            attempted_username = args[0] # Username for the current login attempt

            # Safely get the username of the already logged-in user
            logged_in_username = "another user" # Default message part
            # Ensure current_user_in_registry is an object with a username attribute
            if hasattr(current_user_in_registry, 'username') and isinstance(getattr(current_user_in_registry, 'username', None), str):
                logged_in_username = current_user_in_registry.username
            
            if logged_in_username == attempted_username:
                # Case: Trying to log in as the same user who is already logged in.
                raise AuthenticationError(f"You are already logged in as '{attempted_username}'.")
            else:
                # Case: Trying to log in as a different user while someone else is logged in.
                raise AuthenticationError(
                    f"User '{logged_in_username}' is already logged in. "
                    f"Please logout first if you want to login as '{attempted_username}'."
                )
    
        username, password = args[0], args[1]
        user = self._user_service.authenticate(username, password)
        
        if not user:
            raise AuthenticationError("Invalid username or password")
        
        self._registry.set_current_user(user)  # Обновляем во всем registry
        print(f"Welcome, {username}!")
