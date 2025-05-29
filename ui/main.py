from typing import Optional
from infrastructure.config.cli_config import CLIConfig
from ui.handlers.error_handler import ConsoleErrorHandler

class Application:
    def __init__(self, config: Optional[CLIConfig] = None):
        self.config = config or CLIConfig()
        self.error_handler = ConsoleErrorHandler()

    def run(self) -> None:
        print(self.config.format_message("Welcome to Art Gallery Management System", "info"))
        
        while True:
            try:
                command = input(self.config.prompt_symbol).strip()
                if command.lower() == "exit":
                    print(self.config.format_message("Goodbye!", "info"))
                    break
                
                # Здесь будет выполнение команды
                # self.command_processor.process(command)
                
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
