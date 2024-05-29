from usuario import Usuario


class Administrador(Usuario):
    def __init__(self, identificador, nombre, apellido1, apellido2, hashed_password):
        super().__init__(identificador, nombre, apellido1, apellido2, hashed_password)
