class NoConexionError(Exception):
    def __init__(self, isbn):
        super().__init__(f'No se han podido obtener los datos del libro con ISBN {isbn}')