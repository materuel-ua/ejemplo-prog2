"""
Módulo de excepciones personalizadas para la gestión de libros.

Este módulo define una excepción personalizada `LibroNoEncontradoError` que se utiliza
para manejar casos en los que no se encuentra un libro específico en la colección.

Clases:
    - LibroNoEncontradoError: Excepción personalizada para libros no encontrados.
"""


class LibroNoEncontradoError(Exception):
    """
    Excepción personalizada para indicar que un libro no se ha encontrado en la colección.

    Atributos:
    ----------
    isbn : str
        ISBN del libro que no se ha encontrado.

    Métodos:
    --------
    __init__(self, isbn: str) -> None:
        Inicializa la excepción con el ISBN del libro no encontrado.
    """

    def __init__(self, isbn: str) -> None:
        """
        Inicializa la excepción con un mensaje que incluye el ISBN del libro no encontrado.

        Parámetros:
        -----------
        isbn : str
            ISBN del libro que no se ha encontrado.
        """
        super().__init__(f'No existe el libro con ISBN {isbn}')
