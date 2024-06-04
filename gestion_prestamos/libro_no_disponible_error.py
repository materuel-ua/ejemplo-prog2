"""
Módulo de excepciones personalizadas para la gestión de préstamos de libros.

Este módulo define una excepción personalizada `LibroNoDisponibleError` que se utiliza
para manejar casos en los que un libro no está disponible para préstamo.

Clases:
    - LibroNoDisponibleError: Excepción personalizada para libros no disponibles.
"""

class LibroNoDisponibleError(Exception):
    """
    Excepción personalizada para indicar que un libro no está disponible para préstamo.

    Atributos:
    ----------
    isbn : str
        ISBN del libro que no está disponible.

    Métodos:
    --------
    __init__(self, isbn: str) -> None:
        Inicializa la excepción con el ISBN del libro que no está disponible.
    """
    def __init__(self, isbn: str) -> None:
        """
        Inicializa la excepción con un mensaje que incluye el ISBN del libro que no está disponible.

        Parámetros:
        -----------
        isbn : str
            ISBN del libro que no está disponible.
        """
        super().__init__(f'No está disponible el libro con ISBN {isbn}')