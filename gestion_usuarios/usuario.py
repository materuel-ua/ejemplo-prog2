"""
Módulo para la gestión de usuarios.

Este módulo define una clase `Usuario` que representa a un usuario y proporciona
métodos para acceder y modificar sus atributos, así como para convertir sus datos
a un diccionario.

Clases:
    - Usuario
"""

class Usuario:
    """
    Clase que representa a un usuario.

    Atributos:
    ----------
    identificador : str
        Identificador único del usuario.
    nombre : str
        Nombre del usuario.
    apellido1 : str
        Primer apellido del usuario.
    apellido2 : str
        Segundo apellido del usuario.
    hashed_password : str
        Contraseña hasheada del usuario.

    Métodos:
    --------
    to_dict() -> dict:
        Convierte los atributos del usuario a un diccionario.
    """

    def __init__(self, identificador: str, nombre: str, apellido1: str, apellido2: str, hashed_password: str) -> None:
        """
        Inicializa una instancia de la clase Usuario.

        Parámetros:
        -----------
        identificador : str
            Identificador único del usuario.
        nombre : str
            Nombre del usuario.
        apellido1 : str
            Primer apellido del usuario.
        apellido2 : str
            Segundo apellido del usuario.
        hashed_password : str
            Contraseña hasheada del usuario.
        """
        self._identificador = identificador
        self._nombre = nombre
        self._apellido1 = apellido1
        self._apellido2 = apellido2
        self._hashed_password = hashed_password

    def __repr__(self) -> str:
        """
        Retorna una representación en cadena de la instancia de Usuario.

        Retorna:
        --------
        str
            Representación en cadena de la instancia de Usuario.
        """
        return (f'Usuario(identificador={self._identificador}, nombre={self._nombre}, '
                f'apellido1={self._apellido1}, apellido2={self._apellido2}, hashed_password={self._hashed_password})')

    def __str__(self) -> str:
        """
        Retorna una representación legible en cadena de la instancia de Usuario.

        Retorna:
        --------
        str
            Representación legible en cadena de la instancia de Usuario.
        """
        return f'{self._nombre} {self._apellido1} {self._apellido2}'

    @property
    def identificador(self) -> str:
        """
        Retorna el identificador del usuario.

        Retorna:
        --------
        str
            Identificador del usuario.
        """
        return self._identificador

    @property
    def hashed_password(self) -> str:
        """
        Retorna la contraseña hasheada del usuario.

        Retorna:
        --------
        str
            Contraseña hasheada del usuario.
        """
        return self._hashed_password

    @hashed_password.setter
    def hashed_password(self, value: str) -> None:
        """
        Establece una nueva contraseña hasheada para el usuario.

        Parámetros:
        -----------
        value : str
            Nueva contraseña hasheada del usuario.
        """
        self._hashed_password = value

    @property
    def nombre(self) -> str:
        """
        Retorna el nombre del usuario.

        Retorna:
        --------
        str
            Nombre del usuario.
        """
        return self._nombre

    @nombre.setter
    def nombre(self, value: str) -> None:
        """
        Establece un nuevo nombre para el usuario.

        Parámetros:
        -----------
        value : str
            Nuevo nombre del usuario.
        """
        self._nombre = value

    @property
    def apellido1(self) -> str:
        """
        Retorna el primer apellido del usuario.

        Retorna:
        --------
        str
            Primer apellido del usuario.
        """
        return self._apellido1

    @apellido1.setter
    def apellido1(self, value: str) -> None:
        """
        Establece un nuevo primer apellido para el usuario.

        Parámetros:
        -----------
        value : str
            Nuevo primer apellido del usuario.
        """
        self._apellido1 = value

    @property
    def apellido2(self) -> str:
        """
        Retorna el segundo apellido del usuario.

        Retorna:
        --------
        str
            Segundo apellido del usuario.
        """
        return self._apellido2

    @apellido2.setter
    def apellido2(self, value: str) -> None:
        """
        Establece un nuevo segundo apellido para el usuario.

        Parámetros:
        -----------
        value : str
            Nuevo segundo apellido del usuario.
        """
        self._apellido2 = value

    def to_dict(self) -> dict:
        """
        Convierte los atributos del usuario a un diccionario.

        Retorna:
        --------
        dict
            Diccionario con los atributos del usuario.
        """
        return {
            'identificador': self._identificador,
            'nombre': self._nombre,
            'apellido1': self._apellido1,
            'apellido2': self._apellido2
        }