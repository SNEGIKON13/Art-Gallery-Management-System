from typing import Optional, Dict, Any
from art_gallery.infrastructure.config.cli_config import CLIConfig
from art_gallery.infrastructure.logging.implementations.file_logger import FileLogger
from art_gallery.infrastructure.logging.implementations.composite_logger import CompositeLogger
from art_gallery.infrastructure.logging.implementations.filtered_logger import FilteredLogger
from art_gallery.ui.handlers.error_handler import ConsoleErrorHandler
from art_gallery.ui.command_registry import CommandRegistry
from art_gallery.ui.command_parser import CommandParser
from art_gallery.ui.command_registrar import register_commands
from art_gallery.ui.services import create_real_services # Changed from create_mock_services
from art_gallery.infrastructure.logging.interfaces.logger import LogLevel

class Application:
    def __init__(self, config: Optional[CLIConfig] = None):
        self.config = config or CLIConfig()
        
        # Инициализация логгеров с фильтрацией
        app_logger = FilteredLogger(
            FileLogger("logs/app.log"), 
            {LogLevel.INFO, LogLevel.DEBUG}
        )
        error_logger = FilteredLogger(
            FileLogger("logs/errors.log"), 
            {LogLevel.ERROR, LogLevel.CRITICAL, LogLevel.WARNING}
        )
        
        self.logger = CompositeLogger([app_logger, error_logger])
        
        self.error_handler = ConsoleErrorHandler(self.logger)
        self.command_parser = CommandParser()
        self.command_registry = CommandRegistry(self.command_parser)
        
        self.services = create_real_services() 
        register_commands(self.command_registry, self.services, self.logger)  

    def run(self) -> None:
        self.logger.info("Application started")
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
                self.logger.info("Application terminated by user")
                print(self.config.format_message("\nExiting...", "info"))
                break
            except Exception as e:
                self.error_handler.handle_error(e)

        self.logger.info("Application stopped")

def main() -> None:
    app = Application()
    app.run()

if __name__ == "__main__":
    main()
