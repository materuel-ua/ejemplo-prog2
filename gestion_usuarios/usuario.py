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

    def __str__(self):
        return f'{self._nombre} {self.apellido1} {self.apellido2}'

    @property
    def identificador(self):
        return self._identificador

    @property
    def hashed_password(self):
        return self._hashed_password

    @hashed_password.setter
    def hashed_password(self, value):
        self._hashed_password = value

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, value):
        self._nombre = value

    @property
    def apellido1(self):
        return self._apellido1

    @apellido1.setter
    def apellido1(self, value):
        self._apellido1 = value

    @property
    def apellido2(self):
        return self._apellido2

    @apellido2.setter
    def apellido2(self, value):
        self._apellido2 = value

    def to_dict(self):
        return {'identificador': self._identificador,
                'nombre': self._nombre,
                'apellido1': self._apellido1,
                'apellido2': self._apellido2}
