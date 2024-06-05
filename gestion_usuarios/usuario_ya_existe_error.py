"""
Módulo de excepciones personalizadas para la gestión de usuarios.

Este módulo define una excepción personalizada `UsuarioYaExisteError` que se utiliza
para manejar casos en los que se intenta añadir un usuario que ya existe en la colección.

Clases:
    - UsuarioYaExisteError: Excepción personalizada para usuarios que ya existen.
"""


class UsuarioYaExisteError(Exception):
    """
    Excepción personalizada para indicar que un usuario ya existe en la colección.

    Atributos:
    ----------
    identificador : str
        Identificador del usuario que ya existe.

    Métodos:
    --------
    __init__(self, identificador: str) -> None:
        Inicializa la excepción con el identificador del usuario que ya existe.
    """

    def __init__(self, identificador: str) -> None:
        """
        Inicializa la excepción con un mensaje que incluye el identificador del usuario que ya existe.

        Parámetros:
        -----------
        identificador : str
            Identificador del usuario que ya existe.
        """
        super().__init__(f'Ya existe el usuario con identificador {identificador}')
