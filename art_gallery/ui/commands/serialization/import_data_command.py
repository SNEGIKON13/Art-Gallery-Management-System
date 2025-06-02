import os
from typing import Sequence, Optional, Dict, Any
from datetime import datetime

from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.application.interfaces.exhibition_service import IExhibitionService
from art_gallery.application.interfaces.user_service import IUserService
from art_gallery.infrastructure.factory.serialization_plugin_factory import SerializationPluginFactory
from art_gallery.infrastructure.logging.interfaces.logger import ILogger, LogLevel
from art_gallery.ui.exceptions.command_exceptions import CommandExecutionError
from art_gallery.ui.decorators.admin_only import admin_only
from art_gallery.ui.decorators.transaction import transaction
from art_gallery.ui.decorators.log_command import log_command
from art_gallery.ui.decorators.authenticated import authenticated
from art_gallery.infrastructure.config.cli_config import CLIConfig
from art_gallery.domain.models.artwork import Artwork, ArtworkType
from art_gallery.domain.models.exhibition import Exhibition
from art_gallery.domain.models.user import User, UserRole

class ImportDataCommand(BaseCommand):
    """
    Команда для импорта данных галереи из файла.
    Поддерживает форматы, зарегистрированные в SerializationPluginFactory.
    """

    def __init__(
        self,
        user_service: IUserService,
        artwork_service: IArtworkService,
        exhibition_service: IExhibitionService,
        serialization_factory: SerializationPluginFactory,
        logger: ILogger,
        cli_config: CLIConfig  # Added cli_config
    ):
        super().__init__(user_service) 
        self._artwork_service = artwork_service
        self._exhibition_service = exhibition_service
        self._serialization_factory = serialization_factory
        self._logger = logger
        self._cli_config = cli_config
        try:
            # Ensure plugins are loaded before getting formats
            # SerializationPluginFactory.initialize() # This should be called once at app startup
            self._supported_formats = self._serialization_factory.get_supported_formats()
        except Exception as e:
            self._logger.log(LogLevel.ERROR, f"Failed to get supported formats from factory: {e}")
            self._supported_formats = []

    @admin_only
    @authenticated
    @transaction
    @log_command
    def execute(self, args: Sequence[str]) -> str:
        """
        Выполняет импорт данных из файла.

        Args:
            args: Аргументы команды. Ожидается путь к файлу и опционально формат.
                  Пример: import_data <filepath> [format]

        Returns:
            str: Сообщение о результате выполнения

        Raises:
            CommandExecutionError: В случае ошибок при импорте
        """
        if not args:
            return self.get_usage()

        input_path_arg = args[0]
        format_override_arg = args[1].lower() if len(args) > 1 else None

        filepath_to_import = ""
        actual_file_format = ""

        base_dir_for_relative = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        base_dir_for_relative = os.path.join(base_dir_for_relative, "exports")

        input_filename_base, input_ext_dot = os.path.splitext(input_path_arg)
        input_ext = input_ext_dot[1:].lower() if input_ext_dot else ""

        # Build a list of (filename_to_try, format_to_assume) tuples
        attempts = []

        if format_override_arg:
            if format_override_arg not in self._supported_formats:
                raise CommandExecutionError(f"Указанный формат '{format_override_arg}' не поддерживается. Доступные: {', '.join(self._supported_formats)}")
            # If input has extension, it must match override, or override is used to append
            if input_ext and input_ext != format_override_arg and input_ext in self._supported_formats:
                 self._logger.log(LogLevel.WARNING, f"Расширение файла '{input_ext}' конфликтует с указанным форматом '{format_override_arg}'. Будет использован формат '{format_override_arg}'.")
                 # We'll try input_filename_base + format_override_arg
                 attempts.append((f"{input_filename_base}.{format_override_arg}", format_override_arg))
            elif input_ext and input_ext == format_override_arg:
                attempts.append((input_path_arg, format_override_arg)) # Use original path, format matches
            else: # No input_ext or input_ext is not a supported format
                attempts.append((f"{input_filename_base}.{format_override_arg}", format_override_arg))
        
        if input_ext and input_ext in self._supported_formats:
            # Add if not already added by format_override logic
            if not any(att[0] == input_path_arg and att[1] == input_ext for att in attempts):
                attempts.append((input_path_arg, input_ext))
        
        # If no extension and no override, try default format, then others
        if not input_ext and not format_override_arg:
            default_format = self._cli_config.serialization_config.get('default_format', 'json')
            if default_format in self._supported_formats:
                attempts.append((f"{input_filename_base}.{default_format}", default_format))
            for fmt in self._supported_formats:
                if fmt != default_format: # Avoid duplicate
                    if not any(att[1] == fmt for att in attempts): # Check if format already attempted
                       attempts.append((f"{input_filename_base}.{fmt}", fmt))

        # Last resort: if input_path_arg was given with an unsupported extension, try it as is.
        if input_ext and input_ext not in self._supported_formats:
            if not any(att[0] == input_path_arg for att in attempts):
                attempts.append((input_path_arg, input_ext)) # Format will be validated later
        elif not input_ext and not format_override_arg and not attempts: # case: input_path_arg has no ext, no override, no default formats worked (empty supported_formats?)
             attempts.append((input_path_arg, "")) # Will likely fail, but provides a path to check


        file_found = False
        for fname_try, fmt_assume in attempts:
            current_full_path = fname_try
            if not os.path.isabs(fname_try):
                current_full_path = os.path.join(base_dir_for_relative, fname_try)
            
            self._logger.log(LogLevel.DEBUG, f"Проверка файла: '{current_full_path}' (предполагаемый формат: '{fmt_assume}')")
            if os.path.isfile(current_full_path):
                filepath_to_import = current_full_path
                # Validate assumed format
                _, actual_ext_dot = os.path.splitext(filepath_to_import)
                actual_ext = actual_ext_dot[1:].lower() if actual_ext_dot else ""

                if fmt_assume and fmt_assume == actual_ext and fmt_assume in self._supported_formats:
                    actual_file_format = fmt_assume
                elif actual_ext in self._supported_formats:
                    actual_file_format = actual_ext
                    if fmt_assume and fmt_assume != actual_file_format:
                        self._logger.log(LogLevel.WARNING, f"Предполагаемый формат '{fmt_assume}' не совпадает с расширением файла '{actual_ext}'. Используется формат файла: '{actual_file_format}'.")
                elif format_override_arg and format_override_arg == actual_ext: # if file had no ext, but override matches generated name
                    actual_file_format = format_override_arg
                elif format_override_arg: # File found, but its ext doesn't match override, and override is supported
                    # This implies we found a file like 'backup.json' when 'import backup xml' was called.
                    # This situation should be an error or a very specific warning.
                    # For now, let's prioritize the file's actual extension if supported.
                     raise CommandExecutionError(f"Найден файл '{filepath_to_import}', но его формат '{actual_ext}' не соответствует указанному '{format_override_arg}'.")
                else: # File found, but its extension is not supported or couldn't be determined
                    raise CommandExecutionError(f"Файл '{filepath_to_import}' найден, но его формат '{actual_ext}' не поддерживается или не удалось определить. Поддерживаемые: {', '.join(self._supported_formats)}")
                
                file_found = True
                break
        
        if not file_found:
            self._logger.log(LogLevel.ERROR, f"Файл импорта не найден. Имя: '{input_path_arg}', override: '{format_override_arg}'. Проверенные варианты: {attempts}")
            # Provide a more user-friendly message about what was tried
            tried_paths_str = ", ".join(list(set(att[0] for att in attempts))) # Unique paths
            raise CommandExecutionError(f"Файл не найден: '{input_path_arg}'. Проверены варианты: {tried_paths_str}")

        self._logger.log(LogLevel.INFO, f"Файл для импорта: '{filepath_to_import}', формат: '{actual_file_format}'")

        try:
            deserializer = self._serialization_factory.get_deserializer(actual_file_format)
            data = deserializer.deserialize_from_file(filepath=filepath_to_import)

            self._validate_import_data(data)
            self._logger.log(LogLevel.INFO, f"Data structure validated for import from {filepath_to_import}")

            imported_counts = self._import_data(data['data'])

            success_message = (f"Успешно импортировано: "
                               f"{imported_counts['users']} пользователей, "
                               f"{imported_counts['artworks']} экспонатов, "
                               f"{imported_counts['exhibitions']} выставок.")
            self._logger.log(LogLevel.INFO, success_message)
            return success_message

        except ValueError as ve:
            self._logger.log(LogLevel.ERROR, f"Validation or format error during import: {str(ve)}")
            raise CommandExecutionError(f"Ошибка валидации или формата: {str(ve)}")
        except CommandExecutionError as cee:
            self._logger.log(LogLevel.ERROR, f"Command execution error during import: {str(cee)}")
            raise cee
        except Exception as e:
            self._logger.log(LogLevel.ERROR, f"Unexpected error during import from {filepath_to_import}: {str(e)}", exc_info=True)
            raise CommandExecutionError(f"Непредвиденная ошибка при импорте данных: {str(e)}")

    def _validate_import_data(self, data: Any) -> None:
        if not isinstance(data, dict):
            self._logger.log(LogLevel.ERROR, "Import data is not a dictionary.")
            raise ValueError("Некорректный формат данных: ожидался словарь.")

        required_top_keys = {'version', 'exported_at', 'data'}
        if not required_top_keys.issubset(data.keys()):
            missing_keys = required_top_keys - data.keys()
            self._logger.log(LogLevel.ERROR, f"Missing top-level keys in import data: {missing_keys}")
            raise ValueError(f"Отсутствуют обязательные поля в импортируемых данных: {', '.join(missing_keys)}")

        if not isinstance(data['data'], dict):
            self._logger.log(LogLevel.ERROR, "The 'data' field in import data is not a dictionary.")
            raise ValueError("Поле 'data' должно быть словарем.")
            
        required_data_sections = {'users', 'artworks', 'exhibitions'}
        if not required_data_sections.issubset(data['data'].keys()):
            missing_sections = required_data_sections - data['data'].keys()
            self._logger.log(LogLevel.ERROR, f"Missing data sections in 'data' field: {missing_sections}")
            raise ValueError(f"Некорректная структура данных для импорта. Отсутствуют секции: {', '.join(missing_sections)}")

    def _import_data(self, data_section: Dict[str, list]) -> Dict[str, int]:
        imported_counts = {'users': 0, 'artworks': 0, 'exhibitions': 0}

        for user_data in data_section.get('users', []):
            try:
                username = user_data.get('username')
                password_hash_to_import = user_data.get('password_hash')
                role_str = user_data.get('role')
                created_at_str = user_data.get('created_at')
                last_login_str = user_data.get('last_login') # Optional
                is_active = user_data.get('is_active', True) # Default to True if missing

                if not all([username, password_hash_to_import, role_str, created_at_str]): # is_active can be bool, last_login can be None
                    self._logger.log(LogLevel.WARNING, f"Skipping user import for '{username or 'N/A'}' due to missing critical data (username, password_hash, role, created_at). Data: {user_data}")
                    continue
            
                try:
                    user_role = UserRole[role_str.upper()] if isinstance(role_str, str) else role_str
                    created_at_dt = datetime.fromisoformat(created_at_str)
                    last_login_dt = datetime.fromisoformat(last_login_str) if last_login_str else None
                    if not isinstance(is_active, bool):
                        self._logger.log(LogLevel.WARNING, f"Invalid 'is_active' flag for user '{username}'. Defaulting to True. Value: {is_active}")
                        is_active = True # Default or raise error
                except (ValueError, KeyError) as e_parse:
                    self._logger.log(LogLevel.WARNING, f"Error parsing data for user '{username}': {str(e_parse)}. Data: {user_data}")
                    continue

                existing_user = self._user_service.get_user_by_username(username)
                if not existing_user:
                    self._user_service.add_imported_user(
                        username=username,
                        password_hash=password_hash_to_import,
                        role=user_role,
                        created_at=created_at_dt,
                        last_login=last_login_dt,
                        is_active=is_active
                    )
                    imported_counts['users'] += 1
                    self._logger.log(LogLevel.INFO, f"Imported user: {username}")
                else:
                    self._logger.log(LogLevel.INFO, f"User {username} already exists, skipping import.")
            except Exception as e:
                self._logger.log(LogLevel.WARNING, f"Error importing user {user_data.get('username', 'N/A')}: {str(e)}")

        for artwork_data in data_section.get('artworks', []):
            artwork_title = artwork_data.get('title')
            try:
                if not artwork_title:
                    self._logger.log(LogLevel.WARNING, "Artwork data missing title, skipping.")
                    continue

                artwork_artist = artwork_data.get('artist')
                artwork_year_str = artwork_data.get('year')
                artwork_description = artwork_data.get('description')
                artwork_image_path = artwork_data.get('image_path')
                artwork_type_str = artwork_data.get('type', 'PAINTING') # Default to PAINTING

                if not all([artwork_artist, artwork_year_str, artwork_description]):
                    self._logger.log(LogLevel.WARNING, f"Artwork '{artwork_title}' missing required fields (artist, year, or description), skipping.")
                    continue
                
                try:
                    artwork_year = int(artwork_year_str)
                except ValueError:
                    self._logger.log(LogLevel.WARNING, f"Invalid year format '{artwork_year_str}' for artwork '{artwork_title}', skipping.")
                    continue

                # Проверяем существующие экспонаты только если ID не предоставлен
                if artwork_data.get('id') is None:
                    all_artworks = self._artwork_service.get_all_artworks()
                    existing_artwork = next((aw for aw in all_artworks if aw.title == artwork_title and aw.artist == artwork_artist), None)
                    if existing_artwork:
                        self._logger.log(LogLevel.INFO, f"Artwork '{artwork_title}' by {artwork_artist} already exists, skipping.")
                        continue

                # Если ID предоставлен или экспонат не существует:
                    try:
                        artwork_type_enum = ArtworkType[artwork_type_str.upper()]
                    except KeyError:
                        self._logger.log(LogLevel.WARNING, f"Invalid artwork type '{artwork_type_str}' for {artwork_title}. Defaulting to PAINTING.")
                        artwork_type_enum = ArtworkType.PAINTING
                    
                # Получаем дополнительные поля для импорта
                artwork_id = artwork_data.get('id')
                created_at_str = artwork_data.get('created_at')
                created_at = datetime.fromisoformat(created_at_str) if created_at_str else None
                
                self._artwork_service.add_imported_artwork(
                    title=artwork_title,
                    artist=artwork_artist,
                    year=artwork_year,
                    description=artwork_description,
                    type=artwork_type_enum,
                    image_path=artwork_image_path,
                    created_at=created_at,
                    id=artwork_id
                )
                imported_counts['artworks'] += 1
                self._logger.log(LogLevel.INFO, f"Imported artwork: {artwork_title}")
            except Exception as e:
                self._logger.log(LogLevel.WARNING, f"Error importing artwork {artwork_title or 'N/A'}: {str(e)}")

        for exhibition_data in data_section.get('exhibitions', []):
            try:
                exhibition_title = exhibition_data.get('title')
                if not exhibition_title:
                    self._logger.log(LogLevel.WARNING, "Exhibition data missing title, skipping.")
                    continue

                exhibition_description = exhibition_data.get('description')
                start_date_str = exhibition_data.get('start_date')
                end_date_str = exhibition_data.get('end_date')
                max_capacity_str = exhibition_data.get('max_capacity')

                if not all([exhibition_description, start_date_str, end_date_str]):
                    self._logger.log(LogLevel.WARNING, f"Exhibition '{exhibition_title}' missing required fields, skipping.")
                    continue

                try:
                    start_date = datetime.fromisoformat(start_date_str)
                    end_date = datetime.fromisoformat(end_date_str)
                    max_capacity = int(max_capacity_str) if max_capacity_str else None
                except ValueError as e:
                    self._logger.log(LogLevel.WARNING, f"Date parsing error for exhibition '{exhibition_title}': {str(e)}")
                    continue
                
                # Получаем дополнительные поля для импорта
                exhibition_id = exhibition_data.get('id')
                created_at_str = exhibition_data.get('created_at')
                created_at = datetime.fromisoformat(created_at_str) if created_at_str else None
                artwork_ids = exhibition_data.get('artwork_ids', [])
                visitors = exhibition_data.get('visitors', [])
                
                all_exhibitions = self._exhibition_service.get_all_exhibitions()
                existing_exhibition = next((ex for ex in all_exhibitions if ex.title == exhibition_title), None)
                
                if not existing_exhibition:
                    self._exhibition_service.add_imported_exhibition(
                        title=exhibition_title,
                        description=exhibition_description,
                        start_date=start_date,
                        end_date=end_date,
                        created_at=created_at,
                        max_capacity=max_capacity,
                        artwork_ids=artwork_ids,
                        visitors=visitors,
                        id=exhibition_id
                    )
                    imported_counts['exhibitions'] += 1
                    self._logger.log(LogLevel.INFO, f"Imported exhibition: {exhibition_title}")
                else:
                    self._logger.log(LogLevel.INFO, f"Exhibition '{exhibition_title}' already exists, skipping.")
            except Exception as e:
                self._logger.log(LogLevel.WARNING, f"Error importing exhibition {exhibition_title or 'N/A'}: {str(e)}")
        
        return imported_counts

    def get_name(self) -> str:
        return "import_data"

    def get_description(self) -> str:
        return "Импортирует данные галереи из файла (пользователи, экспонаты, выставки)."

    def get_usage(self) -> str:
        return (
            "import_data <filepath> [format]\n"
            "  <filepath>: Путь к файлу для импорта.\n"
            "  [format]: Опционально, формат файла (например, json, xml). Если не указан, определяется по расширению."
        )

    def get_help(self) -> str:
        formats = ', '.join(self._supported_formats) if self._supported_formats else "не определены"
        return (
            f"Импортирует данные пользователей, экспонатов и выставок из указанного файла.\n"
            f"Поддерживаемые форматы: {formats}.\n"
            f"Если формат не указан, он определяется по расширению файла.\n"
            f"Команда доступна только администраторам.\n"
            f"Пример: import_data exports/backup_20230101_120000.json\n"
            f"Пример: import_data path/to/your/backup.xml xml"
        )
