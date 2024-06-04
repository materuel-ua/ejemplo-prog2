import gestion_usuarios.gestor_usuarios
from gestion_libros.gestor_libros import GestorLibros
from gestion_libros.libro import Libro
from gestion_prestamos.gestor_prestamos import GestorPrestamos
from gestion_usuarios.gestor_usuarios import GestorUsuarios
from informes.generador_informes import generar_carne, generar_ficha, generar_prestamos


if __name__ == '__main__':


    print(generar_prestamos())
