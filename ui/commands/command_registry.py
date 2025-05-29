from typing import Dict, List, Type
from .interfaces.command import ICommand

class CommandRegistry:
    _instance = None
    _commands: Dict[str, ICommand] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, command_class: Type[ICommand]) -> None:
        command = command_class()
        if command.name in self._commands:
            raise ValueError(f"Command '{command.name}' already registered")
        self._commands[command.name] = command

    def get_command(self, name: str) -> ICommand:
        if name not in self._commands:
            raise ValueError(f"Command '{name}' not found")
        return self._commands[name]

    def get_all_commands(self) -> List[ICommand]:
        return list(self._commands.values())
