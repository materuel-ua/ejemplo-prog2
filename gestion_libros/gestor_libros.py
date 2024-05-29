import pickle

from libro_ya_existe_error import LibroYaExisteError
from libro_no_encontrado_error import LibroNoEncontrado
from libro import Libro

PATH_LIBROS = 'libros.pickle'


class GestorLibros:
    def __init__(self):
        self.__libros = self.cargar_libros()


    def cargar_libros(self):
        try:
            with open(PATH_LIBROS, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return []

    def guardar_libros(self):
        with open(PATH_LIBROS, 'wb') as f:
            pickle.dump(self.__libros, f)

    def buscar_libro(self, isbn):
        try:
            return [x for x in self.__libros if x.isbn == isbn][0]
        except IndexError:
            return None

    def add_libro(self, libro):
        if type(libro) is not Libro:
            raise TypeError('No se está añadiendo un libro')
        elif self.buscar_libro(libro.isbn):
            raise LibroYaExisteError(libro)
        else:
            self.__libros.append(libro)

    def __len__(self):
        return len(self.__libros)


    def __getitem__(self, item):
        return self.__libros[item]

    def remove_libro(self, isbn):
        libro_a_eliminar = self.buscar_libro(isbn)

        if libro_a_eliminar:
            del self.__libros[self.__libros.index(libro_a_eliminar)]
        else:
            raise LibroNoEncontrado(isbn)

if __name__ == '__main__':
    l = Libro('9781492056355', 'Fluent Python, 2nd Edition', 'Ramalho, Luciano ',
              "O'Reilly Media, Inc.", '2022')

    gl = GestorLibros()

    l=gl.buscar_libro('9781492056355')

    gl.remove_libro('9781492056355')

    gl.guardar_libros()
