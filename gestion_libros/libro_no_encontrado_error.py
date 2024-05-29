class LibroNoEncontrado(Exception):
    def __init__(self, isbn):
        super().__init__(f'No existe el libro con ISBN {isbn}')
