import shlex
from typing import Tuple, List
from art_gallery.ui.interfaces.command_parser import ICommandParser
from art_gallery.ui.exceptions.command_exceptions import InvalidCommandFormatError

class CommandParser(ICommandParser):
    def parse(self, input_string: str) -> Tuple[str, List[str]]:
        """
        Парсит строку команды в кортеж (команда, [аргументы])
        Использует shlex для корректной обработки кавычек и пробелов
        """
        if not input_string or input_string.isspace():
            raise InvalidCommandFormatError("Empty command")
            
        try:
            # Разбиваем строку, сохраняя аргументы в кавычках как единое целое
            parts = shlex.split(input_string)
            if not parts:
                raise InvalidCommandFormatError("Empty command")
                
            command = parts[0].lower()  # Приводим команду к нижнему регистру
            args = parts[1:] if len(parts) > 1 else []
            
            return command, args
            
        except ValueError as e:
            raise InvalidCommandFormatError(f"Invalid command format: {str(e)}")

    def validate(self, command: str, args: List[str]) -> bool:
        """
        Проверяет базовую валидность команды и аргументов
        """
        if not command:
            return False
            
        # Проверяем, что команда содержит только допустимые символы
        if not command.replace('-', '').replace('_', '').isalnum():
            return False
            
        # Проверяем, что аргументы не пустые
        if any(not arg.strip() for arg in args):
            return False
            
        return True
