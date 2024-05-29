import pickle
from libro_no_disponible import LibroNoDisponible

PATH_PRESTAMOS = 'prestamos.pickle'


class GestionPrestamos:
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
        except IndexError:
            return None

    def add_prestamo(self, isbn, identificador):
        if isbn not in self.__prestamos:
            self.__prestamos[isbn] = identificador
        else:
            raise LibroNoDisponible(f'El libro con ISBN {isbn} ya está prestado al usuario '
                                    f'con identificador {identificador}')


if __name__ == '__main__':
    gp = GestionPrestamos()
    gp.add_prestamo('9781492056355', '1234567890')
    gp.guardar_prestamos()
