import re

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from gestion_libros.gestor_libros import GestorLibros
from gestion_libros.libro import Libro
from gestion_prestamos.gestor_prestamos import GestorPrestamos
from gestion_usuarios.administrador import Administrador
from gestion_usuarios.gestor_usuarios import GestorUsuarios
from gestion_usuarios.usuario import Usuario

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "QrQc3luSLOS9APc"
jwt = JWTManager(app)


@app.route('/test')
@jwt_required()
def test():
    return str(get_jwt_identity())


@app.route('/login', methods=['GET'])
def login():
    identificador = request.args.get('identificador')
    password = request.args.get('password')

    gu = GestorUsuarios()

    u = gu.buscar_usuario(identificador)
    if u and u.hashed_password == gu.hash_password(password):
        return create_access_token(identity=identificador), 200
    else:
        return f'Usuario o contraseña incorrectos', 401


@app.route('/usuario', methods=['POST'])
@jwt_required()
def add_usuario():
    current_user = get_jwt_identity()

    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(current_user), Administrador):
        return 'Solo los administradores pueden crear usuarios', 403

    identificador = request.args.get('identificador')
    nombre = request.args.get('nombre')
    apellido1 = request.args.get('apellido1')
    apellido2 = request.args.get('apellido2')
    password = request.args.get('password')
    administrador = request.args.get('administrador', 'no')

    if not re.search(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
        return (f'La contraseña debe contener un mínimo de ocho caracteres, al menos una letra mayúscula, '
                f'una letra minúscula, un número y un carácter especial.'), 400

    if gu.buscar_usuario(identificador):
        return f'Usuario {identificador} ya existe', 409
    else:
        if administrador == 'si':
            if current_user == '0':
                gu.add_usuario(Administrador(identificador, nombre, apellido1, apellido2, gu.hash_password(password)))
            else:
                return 'Solo el superadministrador pueden crear administradores', 403
        else:
            gu.add_usuario(Usuario(identificador, nombre, apellido1, apellido2, gu.hash_password(password)))
        gu.guardar_usuarios()
        return f'Usuario {identificador} registrado', 200


@app.route('/usuario', methods=['GET'])
@jwt_required()
def get_usuario():
    gu = GestorUsuarios()
    current_user = gu.buscar_usuario(get_jwt_identity())

    if not isinstance(current_user, Administrador):
        return jsonify(current_user.to_dict()), 403
    else:
        identificador = request.args.get('identificador', '')
        if identificador == '':
            return jsonify(current_user.to_dict()), 403
        else:
            u = gu.buscar_usuario(identificador)
            if u:
                return jsonify(u.to_dict()), 403
            else:
                return f'Usuario con identificador {identificador} no encontrado', 404


@app.route('/libro', methods=['POST'])
@jwt_required()
def add_libro():
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden crear libros', 403

    isbn = request.args.get('isbn')
    titulo = request.args.get('titulo')
    autor = request.args.get('autor')
    editorial = request.args.get('editorial')
    anyo = request.args.get('anyo')

    gl = GestorLibros()

    if gl.buscar_libro(isbn):
        return f'Libro con ISBN {isbn} ya existe', 409
    else:
        gl.add_libro(Libro(isbn, titulo, autor, editorial, anyo))
        gl.guardar_libros()
        return f'Libro con ISBN {isbn} creado', 200


@app.route('/libro', methods=['GET'])
@jwt_required(optional=True)
def get_libro():
    gl = GestorLibros()
    gp = GestorPrestamos()
    gu = GestorUsuarios()
    isbn = request.args.get('isbn')

    l = gl.buscar_libro(isbn)
    if l:
        l_dict = l.to_dict()
        if get_jwt_identity() and isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
            usuario = gp.buscar_prestamos(isbn)
            l_dict['usuario'] = gu.buscar_usuario(usuario).to_dict() if usuario else None
        else:
            l_dict['disponible'] = False if gp.buscar_prestamos(isbn) else True
        return jsonify(l_dict), 200
    else:
        return f'Libro con ISBN {isbn} no encontrado', 404


@app.route('/prestamo', methods=['POST'])
@jwt_required()
def add_prestamo():
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden prestar libros', 403

    isbn = request.args.get('isbn')
    identificador = request.args.get('identificador')

    gp = GestorPrestamos()
    prestamo = gp.buscar_prestamos(isbn)
    if prestamo:
        return f'El libro con ISBN {isbn} ya está prestado al usuario {prestamo}', 409
    else:
        gp.add_prestamo(isbn, identificador)
        gp.guardar_prestamos()
        return f'El libro con ISBN {isbn} ha sido prestado al usuario {identificador}', 200


@app.route('/prestamo', methods=['DELETE'])
@jwt_required()
def delete_prestamo():
    isbn = request.args.get('isbn')

    gp = GestorPrestamos()
    prestamo = gp.buscar_prestamos(isbn)
    if prestamo and prestamo == get_jwt_identity():
        gp.remove_prestamo(isbn)
        gp.guardar_prestamos()
        return f'El libro con ISBN {isbn} ha sido devuelto por el usuario {get_jwt_identity()}', 403
    else:
        return f'El libro con ISBN {isbn} no está prestado actualmente al usuario {get_jwt_identity()}', 403


if __name__ == '__main__':
    app.run(debug=True)
