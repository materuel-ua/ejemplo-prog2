"""
Módulo de excepciones personalizadas para la gestión de préstamos de libros.

Este módulo define una excepción personalizada `DevolucionInvalidaError` que se utiliza
para manejar casos en los que una devolución de libro es inválida porque el usuario que 
intenta devolverlo no es el que lo tiene prestado.

Clases:
    - DevolucionInvalidaError: Excepción personalizada para devoluciones inválidas.
"""


class DevolucionInvalidaError(Exception):
    """
    Excepción personalizada para indicar que una devolución de libro es inválida.

    Atributos:
    ----------
    isbn : str
        ISBN del libro que se intenta devolver.
    identificador : str
        Identificador del usuario que intenta devolver el libro.

    Métodos:
    --------
    __init__(self, isbn: str, identificador: str) -> None:
        Inicializa la excepción con el ISBN del libro y el identificador del usuario.
    """

    def __init__(self, isbn: str, identificador: str) -> None:
        """
        Inicializa la excepción con un mensaje que incluye el ISBN del libro y el identificador del usuario.

        Parámetros:
        -----------
        isbn : str
            ISBN del libro que se intenta devolver.
        identificador : str
            Identificador del usuario que intenta devolver el libro.
        """
        super().__init__(
            f'El usuario {identificador} no puede devolver el libro con ISBN {isbn} por estar prestado a otro usuario')
