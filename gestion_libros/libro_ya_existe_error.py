"""
Módulo de excepciones personalizadas para la gestión de libros.

Este módulo define una excepción personalizada `LibroYaExisteError` que se utiliza
para manejar casos en los que se intenta añadir un libro que ya existe en la colección.

Clases:
    - LibroYaExisteError: Excepción personalizada para libros que ya existen.
"""

from gestion_libros.libro import Libro


class LibroYaExisteError(Exception):
    """
    Excepción personalizada para indicar que un libro ya existe en la colección.

    Atributos:
    ----------
    libro : Libro
        El libro que ya existe en la colección.

    Métodos:
    --------
    __init__(self, libro: Libro) -> None:
        Inicializa la excepción con el libro que ya existe.
    """

    def __init__(self, libro: Libro) -> None:
        """
        Inicializa la excepción con un mensaje que incluye el ISBN del libro que ya existe.

        Parámetros:
        -----------
        libro : Libro
            El libro que ya existe en la colección.
        """
        super().__init__(f'Ya existe el libro con ISBN {libro.isbn}')