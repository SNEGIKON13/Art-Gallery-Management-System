from typing import Optional, Dict, Any
from infrastructure.config.cli_config import CLIConfig
from ui.handlers.error_handler import ConsoleErrorHandler
from ui.command_registry import CommandRegistry
from ui.command_parser import CommandParser
from ui.command_registrar import register_commands
from ui.services import create_mock_services  # изменение здесь

class Application:
    def __init__(self, config: Optional[CLIConfig] = None):
        self.config = config or CLIConfig()
        self.error_handler = ConsoleErrorHandler()
        self.command_parser = CommandParser()
        self.command_registry = CommandRegistry(self.command_parser)
        
        # Вызываем функцию напрямую
        self.services = create_mock_services()
        register_commands(self.command_registry, self.services)

    def run(self) -> None:
        print(self.config.format_message("Welcome to Art Gallery Management System", "info"))
        
        while True:
            try:
                command = input(self.config.prompt_symbol).strip()
                if command.lower() == "exit":
                    print(self.config.format_message("Goodbye!", "info"))
                    break
                
                # Выполняем команду
                result = self.command_registry.execute(command)
                if result:
                    print(self.config.format_message(result, "success"))
                
            except KeyboardInterrupt:
                print(self.config.format_message("\nExiting...", "info"))
                break
            except Exception as e:
                self.error_handler.handle_error(e)

def main() -> None:
    app = Application()
    app.run()

if __name__ == "__main__":
    main()
