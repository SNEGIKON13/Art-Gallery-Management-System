import os
import datetime
from typing import Sequence

from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.decorators import admin_only, authenticated, log_command
from art_gallery.application.interfaces.user_service import IUserService
from art_gallery.infrastructure.logging.interfaces.logger import ILogger, LogLevel

class ListExportsCommand(BaseCommand):
    """
    Команда для вывода списка экспортированных файлов.
    """

    def __init__(self, user_service: IUserService, logger: ILogger):
        super().__init__(user_service)
        self._logger = logger
        # Определяем путь к папке exports относительно корня проекта
        # Корень проекта на 4 уровня выше текущего файла
        # (PROJECT_ROOT/art_gallery/ui/commands/serialization/list_exports_command.py)
        self._exports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        self._exports_dir = os.path.join(self._exports_dir, "exports")

    @admin_only
    @authenticated
    @log_command
    def execute(self, args: Sequence[str]) -> str:
        """
        Выполняет листинг экспортированных файлов.

        Args:
            args: Аргументы команды (не используются).

        Returns:
            str: Строка с информацией о файлах или сообщение об ошибке.
        """
        self._logger.log(LogLevel.INFO, f"Attempting to list files in {self._exports_dir}")

        if not os.path.exists(self._exports_dir) or not os.path.isdir(self._exports_dir):
            message = f"Папка экспорта '{self._exports_dir}' не найдена."
            self._logger.log(LogLevel.WARNING, message)
            return message

        try:
            files_info = []
            for filename in os.listdir(self._exports_dir):
                filepath = os.path.join(self._exports_dir, filename)
                if os.path.isfile(filepath):
                    try:
                        stat_info = os.stat(filepath)
                        creation_time = datetime.datetime.fromtimestamp(stat_info.st_ctime) # Время создания
                        # Для большей кроссплатформенности можно использовать st_mtime (время модификации)
                        # modification_time = datetime.datetime.fromtimestamp(stat_info.st_mtime)
                        size_bytes = stat_info.st_size
                        files_info.append({
                            "name": filename,
                            "created": creation_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "size_kb": f"{size_bytes / 1024:.2f} KB"
                        })
                    except Exception as e_stat:
                        self._logger.log(LogLevel.WARNING, f"Could not get stats for file {filepath}: {e_stat}")
            
            if not files_info:
                return f"В папке '{self._exports_dir}' нет экспортированных файлов."

            output_lines = ["Экспортированные файлы:"]
            output_lines.append("{:<40} {:<20} {:<15}".format("Имя файла", "Дата создания", "Размер"))
            output_lines.append("-" * 75)
            for info in sorted(files_info, key=lambda x: x['created'], reverse=True): # Сортировка по дате создания (новые сверху)
                output_lines.append("{:<40} {:<20} {:<15}".format(info['name'], info['created'], info['size_kb']))
            
            return "\n".join(output_lines)

        except Exception as e:
            self._logger.log(LogLevel.ERROR, f"Error listing export files: {str(e)}")
            return f"Ошибка при получении списка файлов: {str(e)}"

    def get_name(self) -> str:
        return "list_exports"

    def get_description(self) -> str:
        return "Lists all exported backup files."

    def get_usage(self) -> str:
        return "list_exports"

    def get_help(self) -> str:
        return ("Lists all files in the exports directory with their creation date and size.\n"
                "Only administrators can use this command.\n"
                "Example: list_exports")

