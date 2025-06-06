from typing import List, Type, Tuple, Dict, Any
from art_gallery.ui.commands.utility.format_command import FormatCommand
from art_gallery.ui.commands.utility.convert_data_command import ConvertDataCommand
from art_gallery.ui.command_registry.command_registry import CommandRegistry
from art_gallery.ui.services import ServiceCollection
from art_gallery.ui.interfaces.command import ICommand
from art_gallery.ui.commands.utility.help_command import HelpCommand
from art_gallery.ui.commands.utility.exit_command import ExitCommand
from art_gallery.ui.commands.utility.stats_command import StatsCommand

from art_gallery.ui.commands.user.login_command import LoginCommand
from art_gallery.ui.commands.user.logout_command import LogoutCommand
from art_gallery.ui.commands.user.register_command import RegisterCommand
from art_gallery.ui.commands.user.change_password_command import ChangePasswordCommand
from art_gallery.ui.commands.user.deactivate_user_command import DeactivateUserCommand
from art_gallery.ui.commands.user.get_user_info_command import GetUserInfoCommand
from art_gallery.ui.commands.user.list_users_command import ListUsersCommand
from art_gallery.ui.commands.user.get_user_command import GetUserCommand

from art_gallery.ui.commands.artwork.add_artwork_command import AddArtworkCommand
from art_gallery.ui.commands.artwork.get_artwork_command import GetArtworkCommand
from art_gallery.ui.commands.artwork.update_artwork_command import UpdateArtworkCommand
from art_gallery.ui.commands.artwork.delete_artwork_command import DeleteArtworkCommand
from art_gallery.ui.commands.artwork.open_artwork_image_command import OpenArtworkImageCommand
from art_gallery.ui.commands.artwork.list_artworks_command import ListArtworksCommand
from art_gallery.ui.commands.artwork.search_artworks_command import SearchArtworksCommand
from art_gallery.ui.commands.artwork.upload_artwork_image_command import UploadArtworkImageCommand

from art_gallery.ui.commands.exhibition.create_exhibition_command import CreateExhibitionCommand
from art_gallery.ui.commands.exhibition.get_exhibition_command import GetExhibitionCommand
from art_gallery.ui.commands.exhibition.update_exhibition_command import UpdateExhibitionCommand
from art_gallery.ui.commands.exhibition.delete_exhibition_command import DeleteExhibitionCommand
from art_gallery.ui.commands.exhibition.list_exhibitions_command import ListExhibitionsCommand
from art_gallery.ui.commands.exhibition.add_artwork_to_exhibition_command import AddArtworkToExhibitionCommand
from art_gallery.ui.commands.exhibition.remove_artwork_from_exhibition_command import RemoveArtworkFromExhibitionCommand

from art_gallery.infrastructure.logging.interfaces.logger import ILogger
from art_gallery.infrastructure.factory.serialization_plugin_factory import SerializationPluginFactory

def register_commands(registry: CommandRegistry, services: ServiceCollection, logger: ILogger) -> None:
    """Регистрирует все доступные команды"""
    commands: List[Tuple[Type[ICommand], Dict[str, Any]]] = [
        # Utility Commands
        (HelpCommand, {"command_registry": registry, "user_service": services.user_service, "cli_config": services.cli_config}),
        (ExitCommand, {"command_registry": registry, "user_service": services.user_service}),
        (StatsCommand, {
            "user_service": services.user_service, 
            "artwork_service": services.artwork_service, 
            "exhibition_service": services.exhibition_service
        }),
        
        # User Commands
        (LoginCommand, {"command_registry": registry, "user_service": services.user_service}),
        (LogoutCommand, {"command_registry": registry, "user_service": services.user_service}),
        (RegisterCommand, {"command_registry": registry, "user_service": services.user_service}),
        (ChangePasswordCommand, {"command_registry": registry, "user_service": services.user_service}),
        (DeactivateUserCommand, {"user_service": services.user_service, "command_registry": registry}),
        (GetUserInfoCommand, {
            "user_service": services.user_service, 
            "command_registry": registry,
            "cli_config": services.cli_config
        }),
        (ListUsersCommand, {"user_service": services.user_service}),
        (GetUserCommand, {"user_service": services.user_service}),
        
        # Artwork Commands
        (AddArtworkCommand, {"artwork_service": services.artwork_service, "user_service": services.user_service}),
        (GetArtworkCommand, {"artwork_service": services.artwork_service, "user_service": services.user_service}),
        (UpdateArtworkCommand, {"artwork_service": services.artwork_service, "user_service": services.user_service}),
        (DeleteArtworkCommand, {"artwork_service": services.artwork_service, "user_service": services.user_service}),
        (OpenArtworkImageCommand, {
            "artwork_service": services.artwork_service, 
            "user_service": services.user_service,
            "cli_config": services.cli_config
        }),
        (UploadArtworkImageCommand, {
            "artwork_service": services.artwork_service, 
            "user_service": services.user_service
        }),
        (ListArtworksCommand, {"artwork_service": services.artwork_service, "user_service": services.user_service}),
        (SearchArtworksCommand, {"artwork_service": services.artwork_service, "user_service": services.user_service}),
        
        # Exhibition Commands
        (CreateExhibitionCommand, {"exhibition_service": services.exhibition_service, "user_service": services.user_service}),
        (GetExhibitionCommand, {
            "exhibition_service": services.exhibition_service,
            "artwork_service": services.artwork_service,
            "user_service": services.user_service
        }),
        (UpdateExhibitionCommand, {"exhibition_service": services.exhibition_service, "user_service": services.user_service}),
        (DeleteExhibitionCommand, {"exhibition_service": services.exhibition_service, "user_service": services.user_service}),
        (ListExhibitionsCommand, {"exhibition_service": services.exhibition_service, "user_service": services.user_service}),
        (AddArtworkToExhibitionCommand, {
            "exhibition_service": services.exhibition_service, 
            "artwork_service": services.artwork_service, 
            "user_service": services.user_service
        }),
        (RemoveArtworkFromExhibitionCommand, {
            "exhibition_service": services.exhibition_service, 
            "artwork_service": services.artwork_service, 
            "user_service": services.user_service
        }),
        
        # Serialization Commands
        (FormatCommand, {
            "command_registry": registry,
            "user_service": services.user_service,
            "serialization_factory": SerializationPluginFactory()
        }),
        (ConvertDataCommand, {
            "command_registry": registry,
            "user_service": services.user_service,
            "serialization_factory": SerializationPluginFactory()
        })
    ]
    
    for command_class, deps in commands:
        command = command_class(**deps)
        registry.register(command)
