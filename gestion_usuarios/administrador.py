"""
Módulo para la gestión de administradores.

Este módulo define una clase `Administrador` que hereda de la clase `Usuario` y 
representa a un administrador del sistema.

Clases:
    - Administrador: Hereda de `Usuario` y representa a un administrador.
"""

from gestion_usuarios.usuario import Usuario


class Administrador(Usuario):
    """
    Clase que representa a un administrador, heredando de la clase Usuario.

    Métodos:
    --------
    __init__(self, identificador: str, nombre: str, apellido1: str, apellido2: str, hashed_password: str) -> None:
        Inicializa una instancia de Administrador.
    """

    def __init__(self, identificador: str, nombre: str, apellido1: str, apellido2: str, hashed_password: str) -> None:
        """
        Inicializa una instancia de la clase Administrador.

        Parámetros:
        -----------
        identificador : str
            Identificador único del administrador.
        nombre : str
            Nombre del administrador.
        apellido1 : str
            Primer apellido del administrador.
        apellido2 : str
            Segundo apellido del administrador.
        hashed_password : str
            Contraseña hasheada del administrador.
        """
        super().__init__(identificador, nombre, apellido1, apellido2, hashed_password)
