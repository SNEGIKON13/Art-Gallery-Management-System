from .error_handler import ConsoleErrorHandler

class Application:
    def __init__(self):
        self.error_handler = ConsoleErrorHandler()

    def run(self):
        while True:
            try:
                command = input("> ").strip()
                if command == "exit":
                    break
                    
                # Здесь будет выполнение команды
                # self.command_processor.process(command)
                
            except Exception as e:
                self.error_handler.handle_error(e)

def main():
    app = Application()
    app.run()

if __name__ == "__main__":
    main()
