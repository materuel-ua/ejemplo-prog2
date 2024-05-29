class Usuario:
    def __init__(self, identificador, nombre, apellido1, apellido2, hashed_password):
        self._identificador = identificador
        self._nombre = nombre
        self._apellido1 = apellido1
        self._apellido2 = apellido2
        self._hashed_password = hashed_password

    def __repr__(self):
        return (f'Usuario(identificador={self._identificador}, nombre={self._nombre}, apellido1={self._apellido1}, '
                f'apellido2={self._apellido2}, hashed_password={self._hashed_password})')

    @property
    def identificador(self):
        return self._identificador

    @property
    def hashed_password(self):
        return self._hashed_password

    def to_dict(self):
        return {'identificador': self._identificador,
                'nombre': self._nombre,
                'apellido1': self._apellido1,
                'apellido2': self._apellido2}
