class PrestamoNoEncontradoError(Exception):
    def __init__(self, isbn):
        super().__init__(f'No existe el préstamo del libro con ISBN {isbn}')
