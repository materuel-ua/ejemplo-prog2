"""
Módulo para la gestión de una colección de libros y sus carátulas.

Este módulo define una clase `GestorLibros` que permite administrar una colección 
de libros, incluyendo operaciones como agregar, eliminar, actualizar y buscar libros, 
así como cargar y guardar la colección en un archivo.

Clases:
    - GestorLibros

Excepciones:
    - LibroYaExisteError: Error personalizado para manejar el caso en que un libro ya existe.
    - LibroNoEncontradoError: Error personalizado para manejar el caso en que un libro no se encuentra.
"""

import glob
import os
import pickle
from typing import List, Optional

from gestion_libros.libro_ya_existe_error import LibroYaExisteError
from gestion_libros.libro_no_encontrado_error import LibroNoEncontradoError
from gestion_libros.libro import Libro
from config import PATH_DATA, PATH_IMAGENES


class GestorLibros:
    """
    Clase que gestiona una colección de libros.

    Métodos:
    --------
    cargar_libros() -> List[Libro]:
        Carga la colección de libros desde un archivo.
    guardar_libros() -> None:
        Guarda la colección de libros en un archivo.
    buscar_libro(isbn: str) -> Optional[Libro]:
        Busca un libro por su ISBN.
    add_libro(libro: Libro) -> None:
        Añade un libro a la colección.
    remove_libro(isbn: str) -> None:
        Elimina un libro de la colección por su ISBN.
    update_libro(isbn: str, titulo: str, autor: str, editorial: str, anyo: str) -> None:
        Actualiza los datos de un libro en la colección.
    buscar_caratula(isbn: str) -> Optional[str]:
        Busca la carátula de un libro por su ISBN.
    """

    def __init__(self) -> None:
        self.__libros: List[Libro] = self.cargar_libros()

    def cargar_libros(self) -> List[Libro]:
        """
        Carga la colección de libros desde un archivo.

        Retorna:
        --------
        List[Libro]
            Lista de libros cargados desde el archivo.
        """
        try:
            with open(PATH_DATA, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return []

    def guardar_libros(self) -> None:
        """
        Guarda la colección de libros en un archivo.
        """
        with open(PATH_DATA, 'wb') as f:
            pickle.dump(self.__libros, f)

    def buscar_libro(self, isbn: str) -> Optional[Libro]:
        """
        Busca un libro por su ISBN.

        Parámetros:
        -----------
        isbn : str
            ISBN del libro a buscar.

        Retorna:
        --------
        Optional[Libro]
            El libro encontrado o None si no se encuentra.
        """
        try:
            return [x for x in self.__libros if x.isbn == isbn][0]
        except IndexError:
            return None

    def add_libro(self, libro: Libro) -> None:
        """
        Añade un libro a la colección.

        Parámetros:
        -----------
        libro : Libro
            El libro a añadir.

        Excepciones:
        ------------
        TypeError:
            Si el objeto a añadir no es una instancia de la clase Libro.
        LibroYaExisteError:
            Si el libro ya existe en la colección.
        """
        if not isinstance(libro, Libro):
            raise TypeError('No se está añadiendo un libro')
        elif self.buscar_libro(libro.isbn):
            raise LibroYaExisteError(libro)
        else:
            self.__libros.append(libro)

    def __len__(self) -> int:
        """
        Retorna la cantidad de libros en la colección.

        Retorna:
        --------
        int
            Cantidad de libros en la colección.
        """
        return len(self.__libros)

    def __getitem__(self, item: int) -> Libro:
        """
        Permite acceder a un libro por su índice.

        Parámetros:
        -----------
        item : int
            Índice del libro en la colección.

        Retorna:
        --------
        Libro
            El libro en la posición indicada.
        """
        return self.__libros[item]

    def remove_libro(self, isbn: str) -> None:
        """
        Elimina un libro de la colección por su ISBN.

        Parámetros:
        -----------
        isbn : str
            ISBN del libro a eliminar.

        Excepciones:
        ------------
        LibroNoEncontradoError:
            Si el libro no se encuentra en la colección.
        """
        libro_a_eliminar = self.buscar_libro(isbn)

        if libro_a_eliminar:
            self.__libros.remove(libro_a_eliminar)
        else:
            raise LibroNoEncontradoError(isbn)

    def update_libro(self, isbn: str, titulo: str, autor: str, editorial: str, anyo: str) -> None:
        """
        Actualiza los datos de un libro en la colección.

        Parámetros:
        -----------
        isbn : str
            ISBN del libro a actualizar.
        titulo : str
            Nuevo título del libro.
        autor : str
            Nuevo autor del libro.
        editorial : str
            Nueva editorial del libro.
        anyo : str
            Nuevo año de publicación del libro.

        Excepciones:
        ------------
        LibroNoEncontradoError:
            Si el libro no se encuentra en la colección.
        """
        libro_a_actualizar = self.buscar_libro(isbn)

        if libro_a_actualizar:
            libro_a_actualizar.titulo = titulo
            libro_a_actualizar.autor = autor
            libro_a_actualizar.editorial = editorial
            libro_a_actualizar.anyo = anyo
        else:
            raise LibroNoEncontradoError(isbn)

    @staticmethod
    def buscar_caratula(isbn: str) -> Optional[str]:
        """
        Busca la carátula de un libro por su ISBN.

        Parámetros:
        -----------
        isbn : str
            ISBN del libro cuya carátula se busca.

        Retorna:
        --------
        Optional[str]
            Ruta al archivo de la carátula si se encuentra, None en caso contrario.
        """
        for infile in glob.glob(os.path.join(PATH_IMAGENES, isbn + '.*')):
            return infile
        return None
