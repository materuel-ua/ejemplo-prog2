class DevolucionInvalidaError(Exception):
    def __init__(self, isbn, identificador):
        super().__init__(f'El usuario {identificador} no puede devolver el libro con ISBN {isbn} por estar prestado a otro usuario')
