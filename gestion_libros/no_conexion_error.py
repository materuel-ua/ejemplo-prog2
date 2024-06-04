"""
Módulo de excepciones personalizadas para la gestión de libros.

Este módulo define una excepción personalizada `NoConexionError` que se utiliza
para manejar casos en los que no se puede obtener la información de un libro debido
a problemas de conexión.

Clases:
    - NoConexionError: Excepción personalizada para problemas de conexión.
"""

class NoConexionError(Exception):
    """
    Excepción personalizada para indicar que no se ha podido obtener la información de un libro debido a problemas de conexión.

    Atributos:
    ----------
    isbn : str
        ISBN del libro cuya información no se ha podido obtener.

    Métodos:
    --------
    __init__(self, isbn: str) -> None:
        Inicializa la excepción con el ISBN del libro cuya información no se ha podido obtener.
    """
    def __init__(self, isbn: str) -> None:
        """
        Inicializa la excepción con un mensaje que incluye el ISBN del libro cuya información no se ha podido obtener.

        Parámetros:
        -----------
        isbn : str
            ISBN del libro cuya información no se ha podido obtener.
        """
        super().__init__(f'No se han podido obtener los datos del libro con ISBN {isbn}')