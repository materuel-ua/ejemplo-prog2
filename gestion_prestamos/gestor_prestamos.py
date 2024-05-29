import pickle
from datetime import datetime

from gestion_prestamos.devolucion_invalida_error import DevolucionInvalidaError
from gestion_prestamos.prestamo_no_encontrado_error import PrestamoNoEncontradoError
from gestion_prestamos.libro_no_disponible_error import LibroNoDisponibleError

PATH_PRESTAMOS = 'data/prestamos.pickle'


class GestorPrestamos:
    def __init__(self):
        self.__prestamos = self.cargar_prestamos()

    def cargar_prestamos(self):
        try:
            with open(PATH_PRESTAMOS, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {}

    def guardar_prestamos(self):
        with open(PATH_PRESTAMOS, 'wb') as f:
            pickle.dump(self.__prestamos, f)

    def buscar_prestamos(self, isbn):
        try:
            return self.__prestamos[isbn]
        except KeyError:
            return None

    def buscar_prestamos_usuario(self, identificador):
        return [x[0] for x in self.__prestamos.items() if x[1]['usuario'] == identificador]

    def add_prestamo(self, isbn, identificador):
        if isbn not in self.__prestamos:
            self.__prestamos[isbn] = {'usuario': identificador, 'fecha': datetime.now()}
        else:
            raise LibroNoDisponibleError(f'El libro con ISBN {isbn} ya está prestado al usuario '
                                    f'con identificador {identificador}')

    def remove_prestamo(self, isbn, identificador):
        if isbn in self.__prestamos:
            if self.__prestamos[isbn]['usuario'] == identificador:
                del self.__prestamos[isbn]
            else:
                raise DevolucionInvalidaError(isbn, identificador)
        else:
            raise PrestamoNoEncontradoError(isbn)

