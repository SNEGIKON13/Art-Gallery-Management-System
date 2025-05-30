from typing import List, Type, Tuple, Dict, Any
from art_gallery.ui.command_registry import CommandRegistry
from art_gallery.ui.services import ServiceCollection
from art_gallery.ui.interfaces.command import ICommand
from art_gallery.ui.commands.utility.help_command import HelpCommand
from art_gallery.ui.commands.utility.exit_command import ExitCommand
from art_gallery.ui.commands.user.login_command import LoginCommand
from art_gallery.ui.commands.user.logout_command import LogoutCommand
from art_gallery.ui.commands.user.register_command import RegisterCommand
from art_gallery.ui.commands.user.change_password_command import ChangePasswordCommand
from art_gallery.ui.commands.user.deactivate_user_command import DeactivateUserCommand
from art_gallery.ui.commands.user.get_user_info_command import GetUserInfoCommand
from art_gallery.ui.commands.artwork.add_artwork_command import AddArtworkCommand
from art_gallery.ui.commands.artwork.get_artwork_command import GetArtworkCommand
from art_gallery.ui.commands.artwork.update_artwork_command import UpdateArtworkCommand
from art_gallery.ui.commands.artwork.delete_artwork_command import DeleteArtworkCommand
from art_gallery.ui.commands.exhibition.create_exhibition_command import CreateExhibitionCommand
from art_gallery.ui.commands.exhibition.get_exhibition_command import GetExhibitionCommand
from art_gallery.ui.commands.exhibition.update_exhibition_command import UpdateExhibitionCommand
from art_gallery.ui.commands.exhibition.delete_exhibition_command import DeleteExhibitionCommand
from art_gallery.ui.commands.exhibition.list_exhibitions_command import ListExhibitionsCommand

def register_commands(registry: CommandRegistry, services: ServiceCollection) -> None:
    """Регистрирует все доступные команды"""
    commands: List[Tuple[Type[ICommand], Dict[str, Any]]] = [
        # Utility Commands
        (HelpCommand, {
            "command_registry": registry, 
            "user_service": services.user_service,
            "cli_config": services.cli_config
        }),
        (ExitCommand, {"user_service": services.user_service}),
        
        # User Commands
        (LoginCommand, {"user_service": services.user_service}),
        (LogoutCommand, {"user_service": services.user_service}),
        (RegisterCommand, {"user_service": services.user_service}),
        (ChangePasswordCommand, {"user_service": services.user_service}),
        (DeactivateUserCommand, {"user_service": services.user_service}),
        (GetUserInfoCommand, {"user_service": services.user_service}),
        
        # Artwork Commands
        (AddArtworkCommand, {"artwork_service": services.artwork_service, "user_service": services.user_service}),
        (GetArtworkCommand, {"artwork_service": services.artwork_service, "user_service": services.user_service}),
        (UpdateArtworkCommand, {"artwork_service": services.artwork_service, "user_service": services.user_service}),
        (DeleteArtworkCommand, {"artwork_service": services.artwork_service, "user_service": services.user_service}),
        
        # Exhibition Commands
        (CreateExhibitionCommand, {"exhibition_service": services.exhibition_service, "user_service": services.user_service}),
        (GetExhibitionCommand, {"exhibition_service": services.exhibition_service, "user_service": services.user_service}),
        (UpdateExhibitionCommand, {"exhibition_service": services.exhibition_service, "user_service": services.user_service}),
        (DeleteExhibitionCommand, {"exhibition_service": services.exhibition_service, "user_service": services.user_service}),
        (ListExhibitionsCommand, {"exhibition_service": services.exhibition_service, "user_service": services.user_service})
    ]
    
    for command_class, deps in commands:
        command = command_class(**deps)
        registry.register(command)
