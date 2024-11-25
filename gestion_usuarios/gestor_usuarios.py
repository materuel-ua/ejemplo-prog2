"""
Módulo para la gestión de usuarios.

Este módulo define una clase `GestorUsuarios` que permite administrar una colección
de usuarios, incluyendo operaciones como agregar, eliminar, actualizar y buscar usuarios,
así como cargar y guardar la colección en un archivo. También proporciona métodos
para la validación y hashing de contraseñas.

Clases:
    - GestorUsuarios

Excepciones:
    - UsuarioNoEncontradoError: Error personalizado para manejar el caso en que un usuario no se encuentra.
    - UsuarioYaExisteError: Error personalizado para manejar el caso en que un usuario ya existe.
"""

import hashlib
import pickle
import re
from typing import List, Optional

from gestion_usuarios.usuario_no_encontrado_error import UsuarioNoEncontradoError
from gestion_usuarios.usuario_ya_existe_error import UsuarioYaExisteError
from gestion_usuarios.usuario import Usuario
from config import PATH_DATA

PATH_USUARIOS = f'{PATH_DATA}/usuarios.pickle'


class GestorUsuarios:
    """
    Clase que gestiona una colección de usuarios.

    Métodos:
    --------
    cargar_usuarios() -> List[Usuario]:
        Carga la colección de usuarios desde un archivo.
    guardar_usuarios() -> None:
        Guarda la colección de usuarios en un archivo.
    buscar_usuario(identificador: str) -> Optional[Usuario]:
        Busca un usuario por su identificador.
    add_usuario(usuario: Usuario) -> None:
        Añade un usuario a la colección.
    remove_usuario(identificador: str) -> None:
        Elimina un usuario de la colección por su identificador.
    update_usuario(identificador: str, nombre: str, apellido1: str, apellido2: str) -> None:
        Actualiza los datos de un usuario en la colección.
    cambiar_password(identificador: str, old_password_hash: str, new_password_hash: str) -> bool:
        Cambia la contraseña de un usuario.
    hash_password(password: str) -> str:
        Genera un hash SHA-256 para una contraseña.
    validar_password(password: str) -> bool:
        Valida que una contraseña cumpla con los requisitos de seguridad.
    """

    def __init__(self) -> None:
        self.__usuarios: List[Usuario] = self.cargar_usuarios()

    def cargar_usuarios(self) -> List[Usuario]:
        """
        Carga la colección de usuarios desde un archivo.

        Retorna:
        --------
        List[Usuario]
            Lista de usuarios cargados desde el archivo.
        """
        try:
            with open(PATH_USUARIOS, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return []

    def guardar_usuarios(self) -> None:
        """
        Guarda la colección de usuarios en un archivo.
        """
        with open(PATH_USUARIOS, 'wb') as f:
            pickle.dump(self.__usuarios, f)

    def buscar_usuario(self, identificador: str) -> Optional[Usuario]:
        """
        Busca un usuario por su identificador.

        Parámetros:
        -----------
        identificador : str
            Identificador del usuario a buscar.

        Retorna:
        --------
        Optional[Usuario]
            El usuario encontrado o None si no se encuentra.
        """
        try:
            return [x for x in self.__usuarios if x.identificador == identificador][0]
        except IndexError:
            return None

    def add_usuario(self, usuario: Usuario) -> None:
        """
        Añade un usuario a la colección.

        Parámetros:
        -----------
        usuario : Usuario
            El usuario a añadir.

        Excepciones:
        ------------
        TypeError:
            Si el objeto a añadir no es una instancia de la clase Usuario.
        UsuarioYaExisteError:
            Si el usuario ya existe en la colección.
        """
        if not isinstance(usuario, Usuario):
            raise TypeError('No se está añadiendo un usuario')
        elif self.buscar_usuario(usuario.identificador):
            raise UsuarioYaExisteError(usuario.identificador)
        else:
            self.__usuarios.append(usuario)

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Genera un hash SHA-256 para una contraseña.

        Parámetros:
        -----------
        password : str
            Contraseña a hashear.

        Retorna:
        --------
        str
            Hash SHA-256 de la contraseña.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def validar_password(password: str) -> bool:
        """
        Valida que una contraseña cumpla con los requisitos de seguridad.

        Parámetros:
        -----------
        password : str
            Contraseña a validar.

        Retorna:
        --------
        bool
            True si la contraseña cumple con los requisitos de seguridad, False en caso contrario.
        """
        return bool(re.search(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password))

    def remove_usuario(self, identificador: str) -> None:
        """
        Elimina un usuario de la colección por su identificador.

        Parámetros:
        -----------
        identificador : str
            Identificador del usuario a eliminar.

        Excepciones:
        ------------
        UsuarioNoEncontradoError:
            Si el usuario no se encuentra en la colección.
        """
        usuario_a_eliminar = self.buscar_usuario(identificador)

        if usuario_a_eliminar:
            self.__usuarios.remove(usuario_a_eliminar)
        else:
            raise UsuarioNoEncontradoError(identificador)

    def update_usuario(self, identificador: str, nombre: str, apellido1: str, apellido2: str) -> None:
        """
        Actualiza los datos de un usuario en la colección.

        Parámetros:
        -----------
        identificador : str
            Identificador del usuario a actualizar.
        nombre : str
            Nuevo nombre del usuario.
        apellido1 : str
            Nuevo primer apellido del usuario.
        apellido2 : str
            Nuevo segundo apellido del usuario.

        Excepciones:
        ------------
        UsuarioNoEncontradoError:
            Si el usuario no se encuentra en la colección.
        """
        usuario_a_actualizar = self.buscar_usuario(identificador)
        if usuario_a_actualizar:
            usuario_a_actualizar.nombre = nombre
            usuario_a_actualizar.apellido1 = apellido1
            usuario_a_actualizar.apellido2 = apellido2
        else:
            raise UsuarioNoEncontradoError(identificador)

    def cambiar_password(self, identificador: str, old_password_hash: str, new_password_hash: str) -> bool:
        """
        Cambia la contraseña de un usuario.

        Parámetros:
        -----------
        identificador : str
            Identificador del usuario.
        old_password_hash : str
            Hash de la contraseña antigua.
        new_password_hash : str
            Hash de la nueva contraseña.

        Retorna:
        --------
        bool
            True si el cambio de contraseña fue exitoso, False en caso contrario.

        Excepciones:
        ------------
        UsuarioNoEncontradoError:
            Si el usuario no se encuentra en la colección.
        """
        usuario_a_actualizar = self.buscar_usuario(identificador)
        if usuario_a_actualizar:
            if old_password_hash == usuario_a_actualizar.hashed_password:
                usuario_a_actualizar.hashed_password = new_password_hash
                return True
            else:
                return False
        else:
            raise UsuarioNoEncontradoError(identificador)
