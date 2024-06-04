from datetime import datetime

import requests
from gestion_libros.no_conexion_error import NoConexionError


class Libro:
    def __init__(self, isbn, titulo, autor, editorial, anyo):
        self.__isbn = isbn
        self.__titulo = titulo
        self.__autor = autor
        self.__editorial = editorial
        self.__anyo = anyo

    @classmethod
    def por_isbn(cls, isbn):
        try:
            r = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}')
            datos_libro = r.json()

            if datos_libro['totalItems'] == 0:
                raise NoConexionError(isbn)
            else:
                datos_libro = datos_libro['items'][0]

            try:
                titulo = datos_libro['volumeInfo']['title']
            except KeyError:
                titulo = ''

            try:
                autor = datos_libro['volumeInfo']['authors'][0]
            except KeyError:
                autor = ''

            try:
                editorial = datos_libro['volumeInfo']['publisher']
            except KeyError:
                editorial = ''

            try:
                anyo = datos_libro['volumeInfo']['publishedDate'][:4]
            except KeyError:
                anyo = ''

            return cls(isbn, titulo, autor, editorial, anyo)

        except requests.exceptions.ConnectionError:
            raise NoConexionError(isbn)

    @property
    def isbn(self):
        return self.__isbn

    @property
    def titulo(self):
        return self.__titulo

    @titulo.setter
    def titulo(self, value):
        self.__titulo = value

    @property
    def autor(self):
        return self.__autor

    @autor.setter
    def autor(self, value):
        self.__autor = value

    @property
    def editorial(self):
        return self.__editorial

    @editorial.setter
    def editorial(self, value):
        self.__editorial = value

    @property
    def anyo(self):
        return self.__anyo

    @anyo.setter
    def anyo(self, value):
        self.__anyo = value

    def __repr__(self):
        return (
            f'Libro(isbn={self.__isbn}, titulo={self.__titulo}, autor={self.__autor}, editorial={self.__editorial}, '
            f'anyo={self.__anyo})')

    def to_dict(self):
        return {
            'isbn': self.__isbn,
            'titulo': self.__titulo,
            'autor': self.__autor,
            'editorial': self.__editorial,
            'anyo': self.__anyo
        }

    def generar_referencias(self):
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
