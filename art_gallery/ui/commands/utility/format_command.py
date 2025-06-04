from typing import List, Sequence, Optional
import os
import logging
import xml.etree.ElementTree as ET
from art_gallery.ui.decorators import admin_only
from art_gallery.ui.interfaces.command import ICommand
from art_gallery.ui.command_registry import CommandRegistry
from art_gallery.application.interfaces.user_service import IUserService
from art_gallery.domain import User
from art_gallery.infrastructure.factory.serialization_plugin_factory import SerializationPluginFactory
from art_gallery.infrastructure.config import ConfigRegistry, SerializationConfig


class FormatCommand(ICommand):
    """Command to switch the data format between JSON and XML. (Admin only)"""
    
    def __init__(self, command_registry: CommandRegistry, user_service: IUserService, 
                 serialization_factory: SerializationPluginFactory):
        self._command_registry = command_registry
        self._user_service = user_service
        self._serialization_factory = serialization_factory
        self._config_registry = ConfigRegistry()
        # Get format from ConfigRegistry (.env)
        try:
            serialization_config = self._config_registry.get_serialization_config()
            self._current_format = serialization_config.format
        except Exception as e:
            logging.warning(f"Error reading format from ConfigRegistry: {e}")
            self._current_format = "json"  # Default value
        self._current_user: Optional[User] = None
    
    def get_name(self) -> str:
        return "format"
        
    def get_description(self) -> str:
        return "Switch data format between JSON and XML"
        
    def get_usage(self) -> str:
        return "format [json|xml]"
    
    def set_current_user(self, user: Optional[User]) -> None:
        self._current_user = user  # type: ignore[assignment]
        
    def get_help(self) -> str:
        return (
            "(Admin only) Command for switching data format between JSON and XML.\n"
            "Usage: format [json|xml]\n"
            "  format - show current data format\n"
            "  format json - switch to JSON format\n"
            "  format xml - switch to XML format"
        )

    @admin_only  
    def execute(self, args: Sequence[str]) -> None:
        available_formats = self._serialization_factory.get_supported_formats()
        
        # If no arguments are provided, show current format and available formats
        if not args:
            print(f"Current data format: {self._current_format.upper()}")
            print(f"Available formats: {', '.join(available_formats)}")
            print(f"Usage: format [json|xml]")
            return
        
        # Get the requested format and check its availability
        requested_format = args[0].lower()
        if requested_format not in available_formats:
            print(f"Error: Format '{requested_format}' is not supported. Available formats: {', '.join(available_formats)}")
            return
        
        # If the format hasn't changed, just inform the user
        if requested_format == self._current_format:
            print(f"The data format is already set to {requested_format.upper()}")
            return
        
        # Perform format switching
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        data_dir = os.path.join(base_dir, 'data')
        
        # Paths to format directories
        old_format_dir = os.path.join(data_dir, self._current_format)
        new_format_dir = os.path.join(data_dir, requested_format)
        
        # Create the new format directory if it doesn't exist
        os.makedirs(new_format_dir, exist_ok=True)
        
        # Paths to files in the current format
        old_users_file = os.path.join(old_format_dir, f'users.{self._current_format}')
        old_artworks_file = os.path.join(old_format_dir, f'artworks.{self._current_format}')
        old_exhibitions_file = os.path.join(old_format_dir, f'exhibitions.{self._current_format}')
        
        # Paths to files in the new format
        new_users_file = os.path.join(new_format_dir, f'users.{requested_format}')
        new_artworks_file = os.path.join(new_format_dir, f'artworks.{requested_format}')
        new_exhibitions_file = os.path.join(new_format_dir, f'exhibitions.{requested_format}')
        
        # Check if files exist for the current format
        old_files_exist = [
            os.path.exists(old_users_file),
            os.path.exists(old_artworks_file),
            os.path.exists(old_exhibitions_file)
        ]
        
        # Check if files already exist for the new format
        new_files_exist = [
            os.path.exists(new_users_file),
            os.path.exists(new_artworks_file),
            os.path.exists(new_exhibitions_file)
        ]
        
        # If files for the new format already exist, inform the user how to switch
        if any(new_files_exist):
            print(f"Existing data files found in {requested_format.upper()} format.")
            print(f"To switch to this format, restart the application with the --format {requested_format} parameter.")
            return
        
        # If files for the current format exist, but files for the new format don't exist,
        # recommend restarting with the new format to trigger conversion or inform about data unavailability.
        if any(old_files_exist) and not any(new_files_exist):
            print(f"Data in {self._current_format.upper()} format might become unavailable after switching to {requested_format.upper()} without conversion.")
            print(f"To correctly switch formats and preserve data, consider exporting data or restarting the application")
            print(f"with the --format {requested_format} parameter, which might trigger data conversion if implemented.")
            # Depending on application logic, direct conversion might be preferred here.
            # For now, we just inform and let the .env update proceed.

        # Attempt to export the data if old files exist
        if any(old_files_exist):
            try:
                self._export_data(self._current_format, requested_format)
                print(f"Data successfully exported from {self._current_format.upper()} to {requested_format.upper()}.")
            except Exception as e:
                logging.error(f"Error exporting data: {e}", exc_info=True)
                print(f"Error exporting data: {e}")
                print(f"Format will not be changed. Please check logs for details.")
                return

        # Update the current format in the application state and .env file
        self._current_format = requested_format
        
        try:
            success = ConfigRegistry.update_env_variable("SERIALIZATION_FORMAT", requested_format)
            print(f"Data format setting changed to: {requested_format.upper()}.")
            if success:
                print(f"The .env file has been updated: SERIALIZATION_FORMAT={requested_format}.")
            else:
                print(f"Warning: Could not update .env file. Manual update might be required.")
        except Exception as e:
            logging.error(f"Error updating .env file: {e}", exc_info=True)
            print(f"Data format setting changed to: {requested_format.upper()}.")
            print(f"Warning: Could not update .env file. Manual update might be required. Error: {e}")
        
        print("To apply changes fully, please restart the application.")
        return

    def _export_data(self, source_format: str, target_format: str) -> None:
        """Exports data from one format to another."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        data_dir = os.path.join(base_dir, 'data')
        
        # Paths to format directories
        source_dir = os.path.join(data_dir, source_format)
        target_dir = os.path.join(data_dir, target_format)
        
        # Create the target format directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        
        # List of files to export
        entities = ['users', 'artworks', 'exhibitions']
        
        # For each entity type
        for entity in entities:
            source_file = os.path.join(source_dir, f'{entity}.{source_format}')
            target_file = os.path.join(target_dir, f'{entity}.{target_format}')
            
            # Skip if the source file doesn't exist
            if not os.path.exists(source_file):
                continue
                
            # Load data from the source file
            source_deserializer = self._serialization_factory.get_deserializer(source_format)
            data = source_deserializer.deserialize_from_file(source_file)
            
            # Save to the target file
            target_serializer = self._serialization_factory.get_serializer(target_format)
            target_serializer.serialize_to_file(data, target_file)
