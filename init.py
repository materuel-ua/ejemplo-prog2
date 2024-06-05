"""
Script de inicialización del sistema, encargado de crear los directorios para el almacenamiento de
datos e imágenes, así como de la creación de super-administrador del sistema

Contiene las siguientes funciones:

    * main - inicializa el sistema
"""

import os
from gestion_usuarios.gestor_usuarios import GestorUsuarios
from gestion_usuarios.administrador import Administrador
from config import PATH_IMAGENES, PATH_DATA, SUPER_ADMIN_PASSWORD
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

    # Crear directorio 'images' si no existe
    try:
        os.mkdir(PATH_IMAGENES)
    except OSError as error:
        print(f"Error al crear el directorio 'images': {error}")

    # Inicializar el gestor de usuarios y añadir un usuario administrador
    try:
        gu = GestorUsuarios()
        gu.add_usuario(Administrador('0', 'admin', 'admin', 'admin',
                                     gu.hash_password(SUPER_ADMIN_PASSWORD)))
        gu.guardar_usuarios()
    except UsuarioYaExisteError:
        print('El usuario super-administrador del sistema ya está creado')


if __name__ == '__main__':
    main()
