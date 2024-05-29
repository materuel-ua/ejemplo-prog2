class LibroYaExisteError(Exception):
    def __init__(self, libro):
        super().__init__(f'Ya existe el libro con ISBN {libro.isbn}')