import hashlib
import pickle

from gestion_usuarios.usuario_no_encontrado_error import UsuarioNoEncontrado
from gestion_usuarios.usuario_ya_existe_error import UsuarioYaExisteError
from gestion_usuarios.usuario import Usuario

PATH_USUARIOS = 'data/usuarios.pickle'


class GestorUsuarios:
    def __init__(self):
        self.__usuarios = self.cargar_usuarios()

    def cargar_usuarios(self):
        try:
            with open(PATH_USUARIOS, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return []

    def guardar_usuarios(self):
        with open(PATH_USUARIOS, 'wb') as f:
            pickle.dump(self.__usuarios, f)

    def buscar_usuario(self, identificador):
        try:
            return [x for x in self.__usuarios if x.identificador == identificador][0]
        except IndexError:
            return None

    def add_usuario(self, usuario):
        if not isinstance(usuario, Usuario):
            raise TypeError('No se está añadiendo un usuario')
        elif self.buscar_usuario(usuario.identificador):
            raise UsuarioYaExisteError(usuario.identificador)
        else:
            self.__usuarios.append(usuario)

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def remove_usuario(self, identificador):
        usuario_a_eliminar = self.buscar_usuario(identificador)

        if usuario_a_eliminar:
            del self.__usuarios[self.__usuarios.index(usuario_a_eliminar)]
        else:
            raise UsuarioNoEncontrado(identificador)


if __name__ == '__main__':
    gu = GestorUsuarios()

    u = Usuario('1234567890', 'Yo', 'También',
              "También", gu.hash_password('nzsdfiljsdfilfjñlsjdfjszdño'))

    gu.add_usuario(u)

    l=gu.buscar_usuario('1234567890')

    gu.remove_usuario('1234567890')

    gu.guardar_usuarios()
