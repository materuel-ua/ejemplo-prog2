import os
from flask import Flask, request, jsonify, send_file
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from gestion_libros import exportacion
from gestion_libros.gestor_libros import GestorLibros
from gestion_libros.libro import Libro
from gestion_libros.libro_no_encontrado_error import LibroNoEncontradoError
from gestion_libros.libro_ya_existe_error import LibroYaExisteError
from gestion_libros.no_conexion_error import NoConexionError
from gestion_prestamos.devolucion_invalida_error import DevolucionInvalidaError
from gestion_prestamos.gestor_prestamos import GestorPrestamos
from gestion_prestamos.libro_no_disponible_error import LibroNoDisponibleError
from gestion_prestamos.prestamo_no_encontrado_error import PrestamoNoEncontradoError
from gestion_usuarios.administrador import Administrador
from gestion_usuarios.gestor_usuarios import GestorUsuarios
from gestion_usuarios.usuario import Usuario
from gestion_usuarios.usuario_no_encontrado_error import UsuarioNoEncontradoError
from gestion_usuarios.usuario_ya_existe_error import UsuarioYaExisteError
from informes.generador_informes import generar_carne, generar_prestamos, generar_ficha

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "QrQc3luSLOS9APc"
app.config["UPLOAD_FOLDER"] = "images"
jwt = JWTManager(app)


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

    if not gu.validar_password(password):
        return (f'La contraseña debe contener un mínimo de ocho caracteres, al menos una letra mayúscula, '
                f'una letra minúscula, un número y un carácter especial'), 400

    try:
        if administrador == 'si':
            if current_user == '0':
                gu.add_usuario(Administrador(identificador, nombre, apellido1, apellido2, gu.hash_password(password)))
            else:
                return 'Solo el superadministrador pueden crear administradores', 403
        else:
            gu.add_usuario(Usuario(identificador, nombre, apellido1, apellido2, gu.hash_password(password)))
        gu.guardar_usuarios()
        return f'Usuario {identificador} registrado', 200
    except UsuarioYaExisteError:
        return f'Usuario {identificador} ya existe', 409


@app.route('/usuario', methods=['PUT'])
@jwt_required()
def update_usuario():
    identificador = get_jwt_identity()
    nombre = request.args.get('nombre')
    apellido1 = request.args.get('apellido1')
    apellido2 = request.args.get('apellido2')
    try:
        gu = GestorUsuarios()
        gu.update_usuario(identificador, nombre, apellido1, apellido2)
        gu.guardar_usuarios()
        return f'Usuario {identificador} actualizado', 200
    except UsuarioNoEncontradoError:
        return f'Usuario {identificador} no encontrado', 404


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


@app.route('/usuario', methods=['DELETE'])
@jwt_required()
def remove_usuario():
    identificador = get_jwt_identity()

    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(identificador), Administrador):
        return 'Solo los administradores pueden eliminar usuarios', 403

    identificador = request.args.get('identificador')

    gp = GestorPrestamos()
    if gp.buscar_prestamos_usuario(identificador):
        return f'No se puede eliminar el usuario {identificador} por tener libros prestados', 409
    else:
        try:
            gu.remove_usuario(identificador)
            gu.guardar_usuarios()
            return f'Usuario {identificador} eliminado', 200
        except UsuarioNoEncontradoError:
            return f'Usuario {identificador} no encontrado', 404


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

    try:
        if titulo and autor and editorial and anyo:
            gl.add_libro(Libro(isbn, titulo, autor, editorial, anyo))
        else:
            try:
                gl.add_libro(Libro.por_isbn(isbn))
            except NoConexionError:
                return f'No se han podido obtener los datos del libro con ISBN {isbn}', 424
        gl.guardar_libros()
        return f'Libro con ISBN {isbn} creado', 200
    except LibroYaExisteError:
        return f'Libro con ISBN {isbn} ya existe', 409


@app.route('/libro', methods=['PUT'])
@jwt_required()
def update_libro():
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden actualizar libros', 403

    isbn = request.args.get('isbn')
    titulo = request.args.get('titulo')
    autor = request.args.get('autor')
    editorial = request.args.get('editorial')
    anyo = request.args.get('anyo')

    gl = GestorLibros()
    gp = GestorPrestamos()

    if gp.buscar_prestamos(isbn):
        return f'No se puede actualizar el libro con ISBN {isbn} por estar prestado', 409

    try:
        gl.update_libro(isbn, titulo, autor, editorial, anyo)
        gl.guardar_libros()
        return f'Libro con ISBN {isbn} actualizado', 200
    except LibroNoEncontradoError:
        return f'Libro con ISBN {isbn} no existe', 404


@app.route('/libro', methods=['DELETE'])
@jwt_required()
def remove_libro():
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden actualizar libros', 403

    isbn = request.args.get('isbn')

    gl = GestorLibros()
    gp = GestorPrestamos()

    if gp.buscar_prestamos(isbn):
        return f'No se puede eliminar el libro con ISBN {isbn} por estar prestado', 409

    try:
        gl.remove_libro(isbn)
        gl.guardar_libros()
        return f'Libro con ISBN {isbn} eliminado', 200
    except LibroNoEncontradoError:
        return f'Libro con ISBN {isbn} no existe', 404


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
            prestamo = gp.buscar_prestamos(isbn)
            if prestamo:
                l_dict['usuario'] = gu.buscar_usuario(prestamo['usuario']).to_dict()
                l_dict['fecha_prestamo'] = prestamo['fecha'].strftime("%d/%m/%Y %H:%M:%S")
            else:
                l_dict['usuario'] = None
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

    try:
        gp.add_prestamo(isbn, identificador)
        gp.guardar_prestamos()
        return f'El libro con ISBN {isbn} ha sido prestado al usuario {identificador}', 200
    except LibroNoDisponibleError:
        return f'El libro con ISBN {isbn} ya está prestado al usuario {identificador}', 409


@app.route('/prestamo', methods=['DELETE'])
@jwt_required()
def remove_prestamo():
    isbn = request.args.get('isbn')
    try:
        gp = GestorPrestamos()
        gp.remove_prestamo(isbn, get_jwt_identity())
        gp.guardar_prestamos()
        return f'El libro con ISBN {isbn} ha sido devuelto por el usuario {get_jwt_identity()}', 403
    except PrestamoNoEncontradoError:
        return f'El libro con ISBN {isbn} no está prestado actualmente', 404
    except DevolucionInvalidaError:
        return f'El libro con ISBN {isbn} no está prestado actualmente al usuario {get_jwt_identity()}', 403


@app.route('/cambiar_password', methods=['PUT'])
@jwt_required()
def cambiar_password():
    gu = GestorUsuarios()

    identificador = get_jwt_identity()
    new_password = request.args.get('new_password')

    if not gu.validar_password(new_password):
        return (f'La contraseña debe contener un mínimo de ocho caracteres, al menos una letra mayúscula, '
                f'una letra minúscula, un número y un carácter especial'), 400

    old_password_hash = gu.hash_password(request.args.get('old_password'))
    new_password_hash = gu.hash_password(new_password)

    usuario_a_actualizar = gu.buscar_usuario(identificador)

    if usuario_a_actualizar.hashed_password == old_password_hash:
        gu.buscar_usuario(identificador).hashed_password = new_password_hash
        gu.guardar_usuarios()
        return 'Contraseña cambiada correctamente'
    else:
        return 'Contraseña antigua incorrecta'


@app.route('/caratula', methods=['POST'])
@jwt_required()
def subir_caratula():
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden subir carátulas', 403

    isbn = request.args.get('isbn')
    gl = GestorLibros()
    if not gl.buscar_libro(isbn):
        return f'Libro con ISBN {isbn} no encontrado', 404

    file = request.files['file']
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], isbn + '.' + file.filename.split('.')[1]))
    return f'Carátula del libro con ISBN {isbn} guardada', 200


@app.route('/caratula', methods=['GET'])
def bajar_pelicula():
    isbn = request.args.get('isbn')
    file = GestorLibros.buscar_caratula(isbn)

    if file is None:
        return f'Libro con ISBN {isbn} no encontrado o sin carátula', 404

    return send_file(file), 200


@app.route('/exportar', methods=['GET'])
def exportar():
    return send_file(exportacion.comprime()), 200


@app.route('/carne', methods=['GET'])
@jwt_required()
def bajar_carne():
    gu = GestorUsuarios()
    return send_file(generar_carne(gu.buscar_usuario(get_jwt_identity()))), 200


@app.route('/ficha', methods=['GET'])
def bajar_ficha():
    isbn = request.args.get('isbn')
    gl = GestorLibros()
    l = gl.buscar_libro(isbn)
    if l:
        return send_file(generar_ficha(l)), 200
    else:
        return f'Libro con ISBN {isbn} no encontrado', 404


@app.route('/informe_prestamos', methods=['GET'])
@jwt_required()
def bajar_informe_prestamos():
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden generar informes de préstamos', 403

    return send_file(generar_prestamos()), 200


@app.route('/referencia', methods=['GET'])
def get_referencia():
    gl = GestorLibros()
    isbn = request.args.get('isbn')
    formato = request.args.get('formato')
    l = gl.buscar_libro(isbn)
    if l:
        try:
            return jsonify(l.generar_referencias()[formato]), 200
        except KeyError:
            return 'Formato de referencia invalido', 400

    else:
        return f'Libro con ISBN {isbn} no encontrado', 404


if __name__ == '__main__':
    app.run(debug=True)
