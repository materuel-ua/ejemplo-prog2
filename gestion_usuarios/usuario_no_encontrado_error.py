"""
Módulo de excepciones personalizadas para la gestión de usuarios.

Este módulo define una excepción personalizada `UsuarioNoEncontradoError` que se utiliza
para manejar casos en los que no se encuentra un usuario específico en la colección.

Clases:
    - UsuarioNoEncontradoError: Excepción personalizada para usuarios no encontrados.
"""


class UsuarioNoEncontradoError(Exception):
    """
    Excepción personalizada para indicar que un usuario no se ha encontrado en la colección.

    Atributos:
    ----------
    identificador : str
        Identificador del usuario que no se ha encontrado.

    Métodos:
    --------
    __init__(self, identificador: str) -> None:
        Inicializa la excepción con el identificador del usuario no encontrado.
    """

    def __init__(self, identificador: str) -> None:
        """
        Inicializa la excepción con un mensaje que incluye el identificador del usuario no encontrado.

        Parámetros:
        -----------
        identificador : str
            Identificador del usuario que no se ha encontrado.
        """
        super().__init__(f'No existe el usuario con identificador {identificador}')
