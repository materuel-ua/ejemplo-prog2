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
