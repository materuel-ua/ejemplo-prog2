class Libro:
    def __init__(self, isbn, titulo, autor, editorial, anyo):
        self.__isbn = isbn
        self.__titulo = titulo
        self.__autor = autor
        self.__editorial = editorial
        self.__anyo = anyo

    @property
    def isbn(self):
        return self.__isbn

    def __repr__(self):
        return (f'Libro(isbn={self.__isbn}, titulo={self.__titulo}, autor={self.__autor}, editorial={self.__editorial}, '
                f'anyo={self.__anyo})')

    def to_dict(self):
        return {
            'isbn': self.__isbn,
            'titulo': self.__titulo,
            'autor': self.__autor,
            'editorial': self.__editorial,
            'anyo': self.__anyo
        }


if __name__ == '__main__':
    l = Libro('9781492056355', 'Fluent Python, 2nd Edition', 'Ramalho, Luciano ',
              "O'Reilly Media, Inc.", '2022')
    print(l)