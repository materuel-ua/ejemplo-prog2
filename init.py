from gestion_usuarios.gestor_usuarios import GestorUsuarios
from gestion_usuarios.administrador import Administrador

ADMIN_PASSWORD = 'UAgCZ646D5l9Vbl'

if __name__ == '__main__':
    gu = GestorUsuarios()
    gu.add_usuario(Administrador('0','admin','admin','admin',gu.hash_password(ADMIN_PASSWORD)))
    gu.guardar_usuarios()