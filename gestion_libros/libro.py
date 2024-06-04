"""
Módulo para la gestión de libros utilizando la API de Google Books.

Este módulo define una clase `Libro` que representa un libro y proporciona métodos 
para obtener información del libro a partir de su ISBN, así como generar citas en 
diferentes formatos (APA, MLA, Chicago, Turabian, IEEE).

Clases:
    - Libro

Excepciones:
    - NoConexionError: Error personalizado para manejar problemas de conexión.
"""

import requests
from gestion_libros.no_conexion_error import NoConexionError

class Libro:
    """
    Clase que representa un libro.

    Atributos:
    ----------
    isbn : str
        ISBN del libro.
    titulo : str
        Título del libro.
    autor : str
        Autor del libro.
    editorial : str
        Editorial del libro.
    anyo : str
        Año de publicación del libro.

    Métodos:
    --------
    por_isbn(isbn: str) -> 'Libro':
        Crea una instancia de Libro a partir de un ISBN.
    generar_referencias() -> dict:
        Genera las citas del libro en diferentes formatos.
    to_dict() -> dict:
        Convierte los atributos del libro a un diccionario.
    """

    def __init__(self, isbn: str, titulo: str, autor: str, editorial: str, anyo: str) -> None:
        """
        Inicializa una instancia de la clase Libro.

        Parámetros:
        -----------
        isbn : str
            ISBN del libro.
        titulo : str
            Título del libro.
        autor : str
            Autor del libro.
        editorial : str
            Editorial del libro.
        anyo : str
            Año de publicación del libro.
        """
        self.__isbn = isbn
        self.__titulo = titulo
        self.__autor = autor
        self.__editorial = editorial
        self.__anyo = anyo

    @classmethod
    def por_isbn(cls, isbn: str) -> 'Libro':
        """
        Crea una instancia de Libro a partir de un ISBN consultando la API de Google Books.

        Parámetros:
        -----------
        isbn : str
            ISBN del libro.

        Retorna:
        --------
        Libro
            Instancia de la clase Libro.

        Excepciones:
        ------------
        NoConexionError:
            Si no se puede conectar a la API de Google Books.
        """
        try:
            r = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}')
            datos_libro = r.json()

            if datos_libro['totalItems'] == 0:
                raise NoConexionError(isbn)
            else:
                datos_libro = datos_libro['items'][0]

            # Obtención de datos del libro con manejo de excepciones
            titulo = datos_libro['volumeInfo'].get('title', '')
            autor = datos_libro['volumeInfo'].get('authors', [''])[0]
            editorial = datos_libro['volumeInfo'].get('publisher', '')
            anyo = datos_libro['volumeInfo'].get('publishedDate', '')[:4]

            return cls(isbn, titulo, autor, editorial, anyo)

        except requests.exceptions.ConnectionError:
            raise NoConexionError(isbn)

    @property
    def isbn(self) -> str:
        return self.__isbn

    @property
    def titulo(self) -> str:
        return self.__titulo

    @titulo.setter
    def titulo(self, value: str) -> None:
        self.__titulo = value

    @property
    def autor(self) -> str:
        return self.__autor

    @autor.setter
    def autor(self, value: str) -> None:
        self.__autor = value

    @property
    def editorial(self) -> str:
        return self.__editorial

    @editorial.setter
    def editorial(self, value: str) -> None:
        self.__editorial = value

    @property
    def anyo(self) -> str:
        return self.__anyo

    @anyo.setter
    def anyo(self, value: str) -> None:
        self.__anyo = value

    def __repr__(self) -> str:
        return (
            f'Libro(isbn={self.__isbn}, titulo={self.__titulo}, autor={self.__autor}, '
            f'editorial={self.__editorial}, anyo={self.__anyo})'
        )

    def to_dict(self) -> dict:
        """
        Convierte los atributos del libro a un diccionario.

        Retorna:
        --------
        dict
            Diccionario con los atributos del libro.
        """
        return {
            'isbn': self.__isbn,
            'titulo': self.__titulo,
            'autor': self.__autor,
            'editorial': self.__editorial,
            'anyo': self.__anyo
        }

    def generar_referencias(self) -> dict:
        """
        Genera las citas del libro en diferentes formatos.

        Retorna:
        --------
        dict
            Diccionario con las citas del libro en los formatos APA, MLA, Chicago, Turabian, IEEE.
        """
        # Formato APA
        apa = f'{self.__autor} ({self.__anyo}). *{self.__titulo}*. {self.__editorial}.'

        # Formato MLA
        mla = f'{self.__autor}. *{self.__titulo}*. {self.__editorial}, {self.__anyo}.'

        # Formato Chicago
        chicago = f'{self.__autor}. {self.__anyo}. *{self.__titulo}*. {self.__editorial}.'

        # Formato Turabian
        turabian = f'{self.__autor}. *{self.__titulo}*. {self.__editorial}, {self.__anyo}.'

        # Formato IEEE
        ieee = f'{self.__autor}, *{self.__titulo}*. {self.__editorial}, {self.__anyo}.'

        return {
            "APA": apa,
            "MLA": mla,
            "Chicago": chicago,
            "Turabian": turabian,
            "IEEE": ieee
        }