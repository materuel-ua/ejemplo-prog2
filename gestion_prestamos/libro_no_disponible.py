class LibroNoDisponible(Exception):
    def __init__(self, isbn):
        super().__init__(f'No está disponible el libro con ISBN {isbn}')