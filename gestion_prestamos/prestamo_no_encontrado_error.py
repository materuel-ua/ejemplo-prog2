"""
Módulo de excepciones personalizadas para la gestión de préstamos de libros.

Este módulo define una excepción personalizada `PrestamoNoEncontradoError` que se utiliza
para manejar casos en los que no se encuentra un préstamo específico en la colección.

Clases:
    - PrestamoNoEncontradoError: Excepción personalizada para préstamos no encontrados.
"""


class PrestamoNoEncontradoError(Exception):
    """
    Excepción personalizada para indicar que un préstamo no se ha encontrado en la colección.

    Atributos:
    ----------
    isbn : str
        ISBN del libro cuyo préstamo no se ha encontrado.

    Métodos:
    --------
    __init__(self, isbn: str) -> None:
        Inicializa la excepción con el ISBN del libro cuyo préstamo no se ha encontrado.
    """

    def __init__(self, isbn: str) -> None:
        """
        Inicializa la excepción con un mensaje que incluye el ISBN del libro cuyo préstamo no se ha encontrado.

        Parámetros:
        -----------
        isbn : str
            ISBN del libro cuyo préstamo no se ha encontrado.
        """
        super().__init__(f'No existe el préstamo del libro con ISBN {isbn}')
