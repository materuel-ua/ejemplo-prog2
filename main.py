"""
Script principal para la aplicación Flask de gestión de biblioteca.

Este script proporciona una API RESTful para gestionar usuarios, libros y préstamos en una biblioteca.
Utiliza JWT para la autenticación y autorización.

Funciones principales:
- Login y logout de usuarios y administradores
- Gestión de usuarios (crear, actualizar, eliminar, obtener)
- Gestión de libros (crear, actualizar, eliminar, obtener)
- Gestión de préstamos (crear, eliminar)
- Subir y descargar carátulas de libros
- Generar y descargar informes, carnés y fichas de libros
- Exportar datos de la biblioteca

Dependencias:
- Flask
- Flask-JWT-Extended
- gestion_libros
- gestion_prestamos
- gestion_usuarios
- informes

Configuraciones:
- JWT_SECRET_KEY: Clave secreta para la generación de tokens JWT
- UPLOAD_FOLDER: Carpeta para almacenar las carátulas de los libros

Ejemplo de uso:
    Ejecutar este módulo directamente para iniciar la aplicación Flask.
    $ python main.py
"""

import os
import sqlite3
from datetime import timedelta, datetime, timezone
from typing import Union

from flask import Flask, request, jsonify, send_file, Response
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, get_jwt
)

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
from config import PATH_IMAGENES, JWT_SECRET_KEY, PATH_DB, PATH_LOG

ACCESS_EXPIRES = timedelta(hours=1)  # Los tokens caducan en una hora
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
app.config["UPLOAD_FOLDER"] = PATH_IMAGENES
jwt = JWTManager(app)


@app.route('/login', methods=['GET'])
def login() -> tuple[str, int]:
    """
    Realiza el login de un usuario y genera un token JWT.

    Obtiene los parámetros `identificador` y `password` desde los argumentos
    de la petición (request.args). Si las credenciales son correctas, se
    genera y retorna un token JWT junto con el código de estado 200. Si no,
    se retorna un mensaje de error y el código de estado 401.

    Además, guarda un registro en un fichero de texto para cada intento de login,
    indicando la fecha/hora, el usuario y si tuvo éxito o fue fallido.

    Returns
    -------
    tuple[str, int]
        - 200: Token JWT si las credenciales son correctas.
        - 401: Mensaje de error si las credenciales son incorrectas.
    """
    identificador = request.args.get('identificador')
    password = request.args.get('password')

    gu = GestorUsuarios()
    u = gu.buscar_usuario(identificador)

    # Verificación de credenciales
    if u and u.hashed_password == gu.hash_password(password):
        status_msg = "Éxito"
        status_code = 200
        response = create_access_token(identity=identificador)
    else:
        status_msg = "Fallido"
        status_code = 401
        response = "Usuario o contraseña incorrectos"

    # Guardar registro en un fichero de log
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(PATH_LOG, "a", encoding="utf-8") as log_file:
        log_file.write(f"{now} | Login de usuario '{identificador}' - {status_msg}\n")

    return response, status_code


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header: dict, jwt_payload: dict) -> bool:
    """
    Verifica si un token se encuentra revocado.

    Esta función es llamada automáticamente por Flask-JWT-Extended en cada
    petición que requiera autenticación. Comprueba en la base de datos si el
    token (identificado por su JTI) ha sido agregado a la lista de tokens revocados.

    Parameters
    ----------
    jwt_header : dict
        Cabecera del token JWT.
    jwt_payload : dict
        Carga útil del token JWT, que incluye el JTI.

    Returns
    -------
    bool
        True si el token se encuentra revocado, False en caso contrario.
    """
    jti = jwt_payload["jti"]
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT jti FROM token WHERE jti = ?", (jti,))
    token = cursor.fetchone()
    conn.close()
    return token is not None


@app.route("/logout", methods=["DELETE"])
@jwt_required()
def modify_token() -> tuple[str, int]:
    """
    Revoca el token JWT del usuario que realiza la solicitud, cerrando su sesión.

    Inserta el JTI del token en la tabla `token` de la base de datos para
    indicarle a la aplicación que debe tratarlo como revocado en peticiones futuras.

    Returns
    -------
    tuple[str, int]
        - 200: Si el token se revoca exitosamente.
        - 409: Si el token ya existe en la base de datos.
    """
    jti = get_jwt()["jti"]
    try:
        conn = sqlite3.connect(PATH_DB)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO token (jti, fecha) VALUES (?, ?)",
            (jti, datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
        )

        conn.commit()
        conn.close()
        return jsonify(msg="JWT revocado"), 200
    except sqlite3.IntegrityError:
        return "Error: El token ya existe en la base de datos.", 409


@app.route('/usuario/<string:identificador>', methods=['POST'])
@jwt_required()
def add_usuario(identificador: str) -> tuple[str, int]:
    """
    Añade un nuevo usuario al sistema. Solo los administradores pueden realizar esta acción.

    Lee los datos del usuario (identificador, nombre, apellido1, apellido2, password)
    desde los argumentos de la solicitud (request.args). Si el parámetro `administrador`
    está en 'si', crea un Administrador (solamente el superadministrador, identificador "0",
    puede realizar esa acción); en caso contrario, crea un Usuario normal.

    Returns
    -------
    tuple[str, int]
        - 200: Mensaje de éxito si se registra el usuario correctamente.
        - 400: Si la contraseña no cumple con los requisitos.
        - 403: Si un administrador diferente al superadministrador intenta crear otro administrador.
        - 409: Si el usuario ya existe.
    """
    current_user = get_jwt_identity()

    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(current_user), Administrador):
        return 'Solo los administradores pueden crear usuarios', 403

    nombre = request.args.get('nombre')
    apellido1 = request.args.get('apellido1')
    apellido2 = request.args.get('apellido2')
    password = request.args.get('password')
    administrador = request.args.get('administrador', 'no')

    if not gu.validar_password(password):
        return (
            'La contraseña debe contener un mínimo de ocho caracteres, al menos '
            'una letra mayúscula, una letra minúscula, un número y un carácter especial'
        ), 400

    try:
        if administrador == 'si':
            if current_user == '0':
                gu.add_usuario(
                    Administrador(
                        identificador,
                        nombre,
                        apellido1,
                        apellido2,
                        gu.hash_password(password)
                    )
                )
            else:
                return 'Solo el superadministrador puede crear administradores', 403
        else:
            gu.add_usuario(
                Usuario(
                    identificador,
                    nombre,
                    apellido1,
                    apellido2,
                    gu.hash_password(password)
                )
            )
        gu.guardar_usuarios()
        return f'Usuario {identificador} registrado', 200
    except UsuarioYaExisteError:
        return f'Usuario {identificador} ya existe', 409


@app.route('/usuario', methods=['PUT'])
@jwt_required()
def update_usuario() -> tuple[str, int]:
    """
    Actualiza la información de un usuario existente.

    El usuario que realiza la solicitud solo puede actualizar sus propios datos.
    Los datos se obtienen desde los argumentos de la solicitud (request.args):
    nombre, apellido1, apellido2.

    Returns
    -------
    tuple[str, int]
        - 200: Mensaje de éxito si se actualiza correctamente.
        - 404: Si el usuario no se encuentra.
    """
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
def get_usuario_actual() -> tuple[dict, int]:
    """
    Obtiene la información de un usuario.

    Si el usuario autenticado no es administrador, solo puede obtener su propia información.
    Si el usuario autenticado es administrador, puede obtener la información de otro usuario
    pasando el argumento `identificador`. Si no se pasa `identificador`, se devolverá la información
    del propio administrador.

    Returns
    -------
    tuple[dict, int]
        - 403: Si se intenta solicitar la información de otro usuario sin ser administrador.
        - 404: Si el usuario consultado no existe.
        - 200: Un diccionario JSON con la información del usuario solicitado (o del mismo usuario).
    """
    gu = GestorUsuarios()
    current_user = gu.buscar_usuario(get_jwt_identity())
    return jsonify(current_user.to_dict()), 200



@app.route('/usuario/<string:identificador>', methods=['GET'])
@jwt_required()
def get_usuario(identificador) -> tuple[dict, int]:
    """
    Obtiene la información de un usuario.

    Si el usuario autenticado no es administrador, solo puede obtener su propia información.
    Si el usuario autenticado es administrador, puede obtener la información de otro usuario
    pasando el argumento `identificador`. Si no se pasa `identificador`, se devolverá la información
    del propio administrador.

    Returns
    -------
    tuple[dict, int]
        - 403: Si se intenta solicitar la información de otro usuario sin ser administrador.
        - 404: Si el usuario consultado no existe.
        - 200: Un diccionario JSON con la información del usuario solicitado (o del mismo usuario).
    """
    gu = GestorUsuarios()
    current_user = gu.buscar_usuario(get_jwt_identity())

    # No administrador
    if not isinstance(current_user, Administrador):
        return 'Solo los administrdores pueden mostrar información de otros usuarios', 403
    else:
        u = gu.buscar_usuario(identificador)
        if u:
            return jsonify(u.to_dict()), 200
        else:
            return f'Usuario con identificador {identificador} no encontrado', 404



@app.route('/usuario', methods=['DELETE'])
@jwt_required()
def remove_usuario() -> tuple[str, int]:
    """
    Elimina un usuario del sistema. Solo los administradores pueden realizar esta acción.

    Verifica que el usuario no tenga libros prestados antes de eliminarlo,
    ya que no se permite eliminar usuarios con préstamos pendientes.

    Returns
    -------
    tuple[str, int]
        - 403: Si el usuario autenticado no es administrador.
        - 404: Si el usuario a eliminar no existe.
        - 409: Si el usuario tiene préstamos pendientes.
        - 200: Mensaje de éxito si se elimina correctamente.
    """
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
def add_libro() -> tuple[str, int]:
    """
    Añade un nuevo libro al sistema. Solo los administradores pueden realizar esta acción.

    Obtiene los datos del libro (isbn, título, autor, editorial, año) desde
    los argumentos de la solicitud (request.args). Si faltan datos, se intenta
    obtener la información a partir del ISBN llamando a `Libro.por_isbn()`,
    que podría requerir una conexión externa (puede fallar).

    Returns
    -------
    tuple[str, int]
        - 200: Mensaje de éxito si se crea el libro correctamente.
        - 403: Si el usuario autenticado no es administrador.
        - 409: Si el libro ya existe.
        - 424: Si no se pueden obtener datos externos para el libro (falla de conexión).
    """
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
            # Intentar obtener datos automáticamente
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
def update_libro() -> tuple[str, int]:
    """
    Actualiza la información de un libro existente. Solo los administradores pueden realizar esta acción.

    Si el libro se encuentra prestado, no se permite actualizar. Los datos
    (título, autor, editorial, año) se obtienen de la solicitud.

    Returns
    -------
    tuple[str, int]
        - 200: Mensaje de éxito si se actualiza el libro.
        - 403: Si el usuario autenticado no es administrador.
        - 404: Si el libro no existe.
        - 409: Si el libro está prestado y no puede actualizarse.
    """
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
def remove_libro() -> tuple[str, int]:
    """
    Elimina un libro del sistema. Solo los administradores pueden realizar esta acción.

    Verifica que el libro no se encuentre prestado antes de eliminarlo.

    Returns
    -------
    tuple[str, int]
        - 200: Mensaje de éxito si se elimina el libro.
        - 403: Si el usuario autenticado no es administrador.
        - 404: Si el libro no existe.
        - 409: Si el libro está prestado y no puede eliminarse.
    """
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden eliminar libros', 403

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
def get_libro() -> tuple[object, int]:
    """
    Obtiene la información de un libro.

    Si el usuario está autenticado y es administrador, se devuelve también
    información sobre si el libro está prestado y a qué usuario. Si el usuario
    no es administrador (o no está autenticado), solo se indica si el libro
    está disponible o no.

    Returns
    -------
    tuple[Union[dict, str], int]
        - 200: Diccionario con la información del libro.
        - 404: Mensaje de error si no se encuentra el libro.
    """
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
            l_dict['disponible'] = not bool(gp.buscar_prestamos(isbn))
        return jsonify(l_dict), 200
    else:
        return f'Libro con ISBN {isbn} no encontrado', 404


@app.route('/prestamo', methods=['POST'])
@jwt_required()
def add_prestamo() -> tuple[str, int]:
    """
    Añade un nuevo préstamo. Solo los administradores pueden realizar esta acción.

    Se obtiene el ISBN del libro y el identificador del usuario desde los argumentos
    de la solicitud (request.args). Si el libro ya está prestado, se responde con un error.

    Returns
    -------
    tuple[str, int]
        - 200: Mensaje de éxito si se presta el libro correctamente.
        - 403: Si el usuario autenticado no es administrador.
        - 409: Si el libro ya está prestado.
    """
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
def remove_prestamo() -> tuple[str, int]:
    """
    Elimina (devuelve) un préstamo. Solo los administradores pueden realizar esta acción.

    Se obtiene el ISBN del libro desde los argumentos de la solicitud (request.args) y
    se utiliza el identificador del token JWT para verificar quién devuelve el libro.
    Si el préstamo no existe o no corresponde al usuario, se devuelve un error.

    Returns
    -------
    tuple[str, int]
        - 200: Mensaje de éxito si se devuelve el libro correctamente.
        - 403: Si el libro no está prestado al usuario que hace la solicitud.
        - 404: Si el libro no está prestado.
    """
    isbn = request.args.get('isbn')
    try:
        gp = GestorPrestamos()
        gp.remove_prestamo(isbn, get_jwt_identity())
        gp.guardar_prestamos()
        return f'El libro con ISBN {isbn} ha sido devuelto por el usuario {get_jwt_identity()}', 200
    except PrestamoNoEncontradoError:
        return f'El libro con ISBN {isbn} no está prestado actualmente', 404
    except DevolucionInvalidaError:
        return f'El libro con ISBN {isbn} no está prestado actualmente al usuario {get_jwt_identity()}', 403


@app.route('/cambiar_password', methods=['PUT'])
@jwt_required()
def cambiar_password() -> tuple[str, int]:
    """
    Cambia la contraseña de un usuario, verificando primero la contraseña antigua.

    Se obtienen la contraseña antigua y la nueva desde los argumentos de la solicitud (request.args).
    Se verifica que la nueva contraseña cumpla con los requisitos de complejidad, y que
    la contraseña antigua coincida con la almacenada.

    Returns
    -------
    tuple[str, int]
        - 200: Si la contraseña se cambia correctamente.
        - 400: Si la contraseña antigua no coincide o la nueva no cumple requisitos.
    """
    gu = GestorUsuarios()

    identificador = get_jwt_identity()
    new_password = request.args.get('new_password')

    if not gu.validar_password(new_password):
        return (
            'La contraseña debe contener un mínimo de ocho caracteres, al menos '
            'una letra mayúscula, una letra minúscula, un número y un carácter especial'
        ), 400

    old_password_hash = gu.hash_password(request.args.get('old_password'))
    new_password_hash = gu.hash_password(new_password)

    usuario_a_actualizar = gu.buscar_usuario(identificador)

    if usuario_a_actualizar.hashed_password == old_password_hash:
        gu.buscar_usuario(identificador).hashed_password = new_password_hash
        gu.guardar_usuarios()
        return 'Contraseña cambiada correctamente', 200
    else:
        return 'Contraseña antigua incorrecta', 400


@app.route('/caratula', methods=['POST'])
@jwt_required()
def subir_caratula() -> tuple[str, int]:
    """
    Sube la carátula de un libro. Solo los administradores pueden realizar esta acción.

    Recibe el archivo de carátula a través de un campo `file` de tipo multipart/form-data.
    El archivo se guarda en la carpeta configurada en `app.config['UPLOAD_FOLDER']` con
    el nombre ISBN.extensión.

    Returns
    -------
    tuple[str, int]
        - 403: Si el usuario autenticado no es administrador.
        - 404: Si el libro no existe.
        - 200: Si se guarda la carátula correctamente.
    """
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden subir carátulas', 403

    isbn = request.args.get('isbn')
    gl = GestorLibros()
    if not gl.buscar_libro(isbn):
        return f'Libro con ISBN {isbn} no encontrado', 404

    file = request.files['file']
    extension = file.filename.rsplit('.', 1)[-1]
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{isbn}.{extension}"))
    return f'Carátula del libro con ISBN {isbn} guardada', 200


@app.route('/caratula', methods=['GET'])
def bajar_caratula() -> tuple[object, int]:
    """
    Descarga la carátula de un libro, si existe.

    El endpoint recibe el ISBN del libro como parámetro `isbn`. Internamente
    se llama a `GestorLibros.buscar_caratula()` para obtener la ruta de la
    carátula.

    Returns
    -------
    tuple[Union[send_file, str], int]
        - 200: Si se encuentra la carátula y se envía el archivo.
        - 404: Si no se encuentra el libro o no tiene carátula.
    """
    isbn = request.args.get('isbn')
    file = GestorLibros.buscar_caratula(isbn)

    if file is None:
        return f'Libro con ISBN {isbn} no encontrado o sin carátula', 404

    return send_file(file), 200


@app.route('/exportar', methods=['GET'])
def exportar() -> tuple[object, int]:
    """
    Exporta los datos de la biblioteca y los comprime en un archivo.

    Llama a la función `exportacion.comprime()` para generar el archivo
    comprimido con los datos (usuarios, libros, préstamos).

    Returns
    -------
    tuple[send_file, int]
        - 200: Retorna el archivo exportado.
    """
    return send_file(exportacion.comprime()), 200


@app.route('/carne', methods=['GET'])
@jwt_required()
def bajar_carne() -> tuple[object, int]:
    """
    Descarga el carné de un usuario autenticado.

    Genera un carné en formato PDF u otro formato configurable con la función
    `generar_carne()`, basándose en la información del usuario autenticado.

    Returns
    -------
    tuple[send_file, int]
        - 200: Retorna el archivo con el carné del usuario.
    """
    gu = GestorUsuarios()
    return send_file(generar_carne(gu.buscar_usuario(get_jwt_identity()))), 200


@app.route('/ficha', methods=['GET'])
def bajar_ficha() -> tuple[object, int]:
    """
    Descarga la ficha de un libro (por ejemplo, en formato PDF).

    Para generar la ficha, se obtiene el libro a partir del ISBN
    (mediante `request.args.get('isbn')`) y luego se llama a `generar_ficha()`.

    Returns
    -------
    tuple[Union[send_file, str], int]
        - 200: Retorna el archivo con la ficha del libro.
        - 404: Si no se encuentra el libro.
    """
    isbn = request.args.get('isbn')
    gl = GestorLibros()
    l = gl.buscar_libro(isbn)
    if l:
        return send_file(generar_ficha(l)), 200
    else:
        return f'Libro con ISBN {isbn} no encontrado', 404


@app.route('/informe_prestamos', methods=['GET'])
@jwt_required()
def bajar_informe_prestamos() -> tuple[object, int]:
    """
    Descarga un informe de préstamos en formato PDF u otro formato definido.

    Solo los administradores pueden generar informes de préstamos. Se llama a
    `generar_prestamos()` para generar el archivo.

    Returns
    -------
    tuple[Union[send_file, str], int]
        - 200: Retorna el archivo con el informe.
        - 403: Si el usuario autenticado no es administrador.
    """
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden generar informes de préstamos', 403

    return send_file(generar_prestamos()), 200


@app.route('/referencia', methods=['GET'])
def get_referencia() -> tuple[object, int]:
    """
    Obtiene la referencia de un libro en un formato específico.

    El formato se obtiene desde request.args.get('formato'). Se llama a la función
    `generar_referencias()` del libro, la cual retorna un diccionario con distintas
    posibles referencias (APA, MLA, etc.).

    Returns
    -------
    tuple[Union[dict, str], int]
        - 200: Retorna la referencia en el formato solicitado.
        - 400: Si el formato no es válido.
        - 404: Si no se encuentra el libro.
    """
    gl = GestorLibros()
    isbn = request.args.get('isbn')
    formato = request.args.get('formato')
    l = gl.buscar_libro(isbn)
    if l:
        try:
            return jsonify(l.generar_referencias()[formato]), 200
        except KeyError:
            return 'Formato de referencia inválido', 400
    else:
        return f'Libro con ISBN {isbn} no encontrado', 404

@app.route('/log', methods=['GET'])
@jwt_required()
def bajar_log() -> tuple[object, int]:
    """
    Descarga el fichero de registro (log) de los inicios de sesión del sistema.

    Solo los usuarios con privilegios de administrador pueden descargar el log.
    Si el usuario no es administrador, se devuelve un mensaje de error y el código
    de estado 403.

    Returns
    -------
    tuple[Union[Response, str], int]
        - (Response, 200) : El fichero de log si el usuario es administrador.
        - (str, 403)      : Mensaje de error si el usuario no es administrador.
    """
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden descargar el log', 403

    return send_file(PATH_LOG), 200

if __name__ == '__main__':
    app.run(debug=True)