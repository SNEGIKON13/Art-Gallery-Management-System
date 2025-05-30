from typing import Dict, Type, List, Optional
from art_gallery.ui.interfaces.command import ICommand
from art_gallery.ui.interfaces.command_parser import ICommandParser
from art_gallery.ui.exceptions.command_exceptions import CommandNotFoundError, CommandExecutionError

class CommandRegistry:
    def __init__(self, parser: ICommandParser):
        self._commands: Dict[str, ICommand] = {}  # Теперь храним экземпляры
        self._parser = parser
        self._current_user = None
        
    def register(self, command: ICommand) -> None:
        """Регистрирует команду в реестре"""
        self._commands[command.get_name().lower()] = command
        
    def execute(self, command_input: str) -> str:
        """Выполняет команду"""
        try:
            command_name, args = self._parser.parse(command_input)
            if command_name not in self._commands:
                raise CommandNotFoundError(f"Команда '{command_name}' не найдена")
                
            return self._commands[command_name].execute(args) or ""
            
        except Exception as e:
            raise CommandExecutionError(str(e))
        
    def get_command_instance(self, command_name: str) -> ICommand:
        """Возвращает экземпляр команды"""
        if command_name not in self._commands:
            raise CommandNotFoundError(f"Команда '{command_name}' не найдена")
            
        return self._commands[command_name]

    def get_commands(self) -> List[str]:
        """Возвращает список всех зарегистрированных команд"""
        return list(self._commands.keys())
    
    def set_current_user(self, user) -> None:
        """Устанавливает текущего пользователя"""
        self._current_user = user
        # Обновляем текущего пользователя во всех командах
        for command in self._commands.values():
            command.set_current_user(user)
    
    def get_current_user(self):
        """Возвращает текущего пользователя"""
        return self._current_user
