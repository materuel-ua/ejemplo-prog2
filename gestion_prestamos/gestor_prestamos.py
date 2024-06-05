"""
Módulo para la gestión de préstamos de libros.

Este módulo define una clase `GestorPrestamos` que permite administrar una colección 
de préstamos de libros, incluyendo operaciones como agregar, eliminar, buscar préstamos, 
así como cargar y guardar la colección en un archivo.

Clases:
    - GestorPrestamos

Excepciones:
    - DevolucionInvalidaError: Error personalizado para manejar el caso en que una devolución es inválida.
    - PrestamoNoEncontradoError: Error personalizado para manejar el caso en que un préstamo no se encuentra.
    - LibroNoDisponibleError: Error personalizado para manejar el caso en que un libro no está disponible.
"""

import pickle
from datetime import datetime
from typing import Dict, List, Optional

from gestion_prestamos.devolucion_invalida_error import DevolucionInvalidaError
from gestion_prestamos.prestamo_no_encontrado_error import PrestamoNoEncontradoError
from gestion_prestamos.libro_no_disponible_error import LibroNoDisponibleError
from config import PATH_DATA


class GestorPrestamos:
    """
    Clase que gestiona una colección de préstamos de libros.

    Métodos:
    --------
    cargar_prestamos() -> Dict[str, dict]:
        Carga la colección de préstamos desde un archivo.
    guardar_prestamos() -> None:
        Guarda la colección de préstamos en un archivo.
    buscar_prestamos(isbn: str) -> Optional[dict]:
        Busca los préstamos de un libro por su ISBN.
    buscar_prestamos_usuario(identificador: str) -> List[str]:
        Busca los préstamos de un usuario por su identificador.
    add_prestamo(isbn: str, identificador: str) -> None:
        Añade un préstamo a la colección.
    remove_prestamo(isbn: str, identificador: str) -> None:
        Elimina un préstamo de la colección.
    len() -> int:
        Retorna la cantidad de préstamos en la colección.
    __getitem__(self, item: int) -> tuple:
        Permite acceder a un préstamo por su índice.
    """

    def __init__(self) -> None:
        self.__prestamos: Dict[str, dict] = self.cargar_prestamos()

    def cargar_prestamos(self) -> Dict[str, dict]:
        """
        Carga la colección de préstamos desde un archivo.

        Retorna:
        --------
        Dict[str, dict]
            Diccionario con los préstamos cargados desde el archivo.
        """
        try:
            with open(PATH_DATA, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {}

    def guardar_prestamos(self) -> None:
        """
        Guarda la colección de préstamos en un archivo.
        """
        with open(PATH_DATA, 'wb') as f:
            pickle.dump(self.__prestamos, f)

    def buscar_prestamos(self, isbn: str) -> Optional[dict]:
        """
        Busca los préstamos de un libro por su ISBN.

        Parámetros:
        -----------
        isbn : str
            ISBN del libro a buscar.

        Retorna:
        --------
        Optional[dict]
            Diccionario con los datos del préstamo si se encuentra, None en caso contrario.
        """
        try:
            return self.__prestamos[isbn]
        except KeyError:
            return None

    def buscar_prestamos_usuario(self, identificador: str) -> List[str]:
        """
        Busca los préstamos de un usuario por su identificador.

        Parámetros:
        -----------
        identificador : str
            Identificador del usuario a buscar.

        Retorna:
        --------
        List[str]
            Lista de ISBNs de los libros prestados al usuario.
        """
        return [isbn for isbn, prestamo in self.__prestamos.items() if prestamo['usuario'] == identificador]

    def add_prestamo(self, isbn: str, identificador: str) -> None:
        """
        Añade un préstamo a la colección.

        Parámetros:
        -----------
        isbn : str
            ISBN del libro a prestar.
        identificador : str
            Identificador del usuario que toma el préstamo.

        Excepciones:
        ------------
        LibroNoDisponibleError:
            Si el libro ya está prestado.
        """
        if isbn not in self.__prestamos:
            self.__prestamos[isbn] = {'usuario': identificador, 'fecha': datetime.now()}
        else:
            raise LibroNoDisponibleError(f'El libro con ISBN {isbn} ya está prestado al usuario '
                                         f'con identificador {identificador}')

    def remove_prestamo(self, isbn: str, identificador: str) -> None:
        """
        Elimina un préstamo de la colección.

        Parámetros:
        -----------
        isbn : str
            ISBN del libro a devolver.
        identificador : str
            Identificador del usuario que devuelve el libro.

        Excepciones:
        ------------
        DevolucionInvalidaError:
            Si el usuario que intenta devolver el libro no es el que lo tiene prestado.
        PrestamoNoEncontradoError:
            Si el préstamo no se encuentra en la colección.
        """
        if isbn in self.__prestamos:
            if self.__prestamos[isbn]['usuario'] == identificador:
                del self.__prestamos[isbn]
            else:
                raise DevolucionInvalidaError(isbn, identificador)
        else:
            raise PrestamoNoEncontradoError(isbn)

    def len(self) -> int:
        """
        Retorna la cantidad de préstamos en la colección.

        Retorna:
        --------
        int
            Cantidad de préstamos en la colección.
        """
        return len(self.__prestamos)

    def __getitem__(self, item: int) -> tuple:
        """
        Permite acceder a un préstamo por su índice.

        Parámetros:
        -----------
        item : int
            Índice del préstamo en la colección.

        Retorna:
        --------
        tuple
            Tupla con el ISBN y los datos del préstamo.
        """
        lista_prestamos = list(self.__prestamos.items())
        return lista_prestamos[item]
