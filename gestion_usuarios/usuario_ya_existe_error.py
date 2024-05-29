class UsuarioYaExisteError(Exception):
    def __init__(self, usuario):
        super().__init__(f'Ya existe el usuario con identificador {usuario.identificador}')