class SerializationError(Exception):
    """Исключение, возникающее при ошибках сериализации"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class DeserializationError(Exception):
    """Исключение, возникающее при ошибках десериализации"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
