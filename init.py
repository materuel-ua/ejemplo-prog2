"""
Script de inicialización del sistema, encargado de crear los directorios para el almacenamiento de
datos e imágenes, así como de la creación de super-administrador del sistema

Contiene las siguientes funciones:

    * main - inicializa el sistema
"""

import os
from gestion_usuarios.gestor_usuarios import GestorUsuarios
from gestion_usuarios.administrador import Administrador

ADMIN_PASSWORD = 'UAgCZ646D5l9Vbl'


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
        os.mkdir('data')
    except OSError as error:
        print(f"Error al crear el directorio 'data': {error}")

    # Crear directorio 'images' si no existe
    try:
        os.mkdir('images')
    except OSError as error:
        print(f"Error al crear el directorio 'images': {error}")

    # Inicializar el gestor de usuarios y añadir un usuario administrador
    gu = GestorUsuarios()
    gu.add_usuario(Administrador('0', 'admin', 'admin', 'admin',
                                 gu.hash_password(ADMIN_PASSWORD)))
    gu.guardar_usuarios()


if __name__ == '__main__':
    main()
