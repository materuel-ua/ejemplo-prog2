"""
Script de inicialización del sistema, encargado de crear los directorios para el almacenamiento de
datos e imágenes, así como de la creación de super-administrador del sistema

Contiene las siguientes funciones:

    * main - inicializa el sistema
"""

import os
import sqlite3
from gestion_libros.gestor_libros import GestorLibros
from gestion_libros.libro import Libro
from gestion_libros.libro_ya_existe_error import LibroYaExisteError
from gestion_prestamos.gestor_prestamos import GestorPrestamos
from gestion_prestamos.libro_no_disponible_error import LibroNoDisponibleError
from gestion_usuarios.gestor_usuarios import GestorUsuarios
from gestion_usuarios.administrador import Administrador, Usuario
from config import PATH_IMAGENES, PATH_DATA, SUPER_ADMIN_PASSWORD, USER_PASSWORD, PATH_DB
from gestion_usuarios.usuario_ya_existe_error import UsuarioYaExisteError


def main() -> None:
    """
    Función principal que inicializa el sistema de gestión de usuarios y directorios necesarios.

    Crea los directorios 'data' e 'images' si no existen. Luego, crea un usuario administrador
    con una contraseña predefinida y guarda los usuarios en el sistema.

    Returns
    -------
    None
    """
    # Crear directorio 'data' si no existe
    try:
        os.mkdir(PATH_DATA)
    except OSError as error:
        print(f"Error al crear el directorio 'data': {error}")

    # Inicializar el gestor de usuarios y añadir un usuario administrador y otro normal
    gu = GestorUsuarios()
    try:
        gu.add_usuario(Administrador('0', 'admin', 'admin', 'admin',
                                     gu.hash_password(SUPER_ADMIN_PASSWORD)))
        gu.guardar_usuarios()
    except UsuarioYaExisteError:
        print('El usuario super-administrador del sistema ya está creado')

    try:
        gu.add_usuario(Usuario('1', 'user', 'user', 'user',
                               gu.hash_password(USER_PASSWORD)))
        gu.guardar_usuarios()
    except UsuarioYaExisteError:
        print('El usuario básico del sistema ya está creado')

    # Inicializar el gestor de libros y añadir un libro de ejemplo
    gl = GestorLibros()
    try:
        gl.add_libro(
            Libro('978-1491946008', 'Fluent Python: Clear, Concise, and Effective Programming', 'Luciano Ramalho',
                  "O'Reilly Media", '2015'))
        gl.guardar_libros()
    except LibroYaExisteError:
        print('El libro de ejemplo ya está creado')

    # Inicializar el gestor de préstamos y prestar el libro de ejemplo al usuario básico del sistema
    gp = GestorPrestamos()
    try:
        gp.add_prestamo('978-1491946008','1')
        gp.guardar_prestamos()
    except LibroNoDisponibleError:
        print('El libro de ejemplo no puede ser prestado')

    # Conectar a la base de datos (o crearla si no existe)
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()

    # Crear la tabla 'token' si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS token (
            jti TEXT PRIMARY KEY,
            fecha DATETIME
        )
    ''')

    # Confirmar cambios y cerrar conexión
    conn.commit()
    conn.close()
    print("Base de datos y tabla 'token' creadas correctamente.")


if __name__ == '__main__':
    main()
