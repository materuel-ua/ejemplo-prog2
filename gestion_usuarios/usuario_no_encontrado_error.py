class UsuarioNoEncontradoError(Exception):
    def __init__(self, identificador):
        super().__init__(f'No existe el usuario con identificador {identificador}')
