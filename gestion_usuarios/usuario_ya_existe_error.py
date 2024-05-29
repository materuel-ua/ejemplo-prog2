class UsuarioYaExisteError(Exception):
    def __init__(self, identificador):
        super().__init__(f'Ya existe el usuario con identificador {identificador}')