"""
Script principal para la aplicación Flask de gestión de biblioteca.

Proporciona una API RESTful para gestionar usuarios, libros y préstamos en una biblioteca.
Utiliza JWT para la autenticación y autorización.

Funciones principales
---------------------
- Login y logout de usuarios y administradores
- Gestión de usuarios (crear, actualizar, eliminar, obtener)
- Gestión de libros (crear, actualizar, eliminar, obtener)
- Gestión de préstamos (crear, eliminar)
- Subir y descargar carátulas de libros
- Generar y descargar informes, carnés y fichas de libros
- Exportar datos de la biblioteca

Dependencias
------------
- Flask
- Flask-JWT-Extended
- gestion_libros
- gestion_prestamos
- gestion_usuarios
- informes

Configuraciones
---------------
- JWT_SECRET_KEY: Clave secreta para la generación de tokens JWT
- UPLOAD_FOLDER: Carpeta para almacenar las carátulas de los libros

Ejemplo de uso
--------------
Para iniciar la aplicación Flask:
>>> python main.py
"""

import os
import sqlite3
from datetime import timedelta, datetime, timezone
from typing import Union, Tuple, Dict, Any

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
def login() -> Tuple[Union[str, Dict[str, Any]], int]:
    """
    Realiza el login de un usuario y genera un token JWT.

    Obtiene los parámetros `identificador` y `password` desde los argumentos
    de la petición (request.args). Si las credenciales son correctas, se genera
    y retorna un token JWT junto con el código de estado 200. En caso contrario,
    se retorna un mensaje de error y el código de estado 401.

    Además, se registra en un fichero de log cada intento de inicio de sesión,
    indicando fecha/hora, usuario y resultado.

    Returns
    -------
    Tuple[Union[str, Dict[str, Any]], int]
        Un par (respuesta, código de estado). Si las credenciales son correctas,
        la respuesta es el token JWT y el código 200. Si son incorrectas, la
        respuesta es un mensaje de error y el código 401.
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
def check_if_token_revoked(jwt_header: Dict[str, Any], jwt_payload: Dict[str, Any]) -> bool:
    """
    Verifica si un token se encuentra revocado.

    Comprueba en la base de datos si el token (identificado por su JTI)
    ha sido agregado a la lista de tokens revocados.

    Parameters
    ----------
    jwt_header : Dict[str, Any]
        Cabecera del token JWT.
    jwt_payload : Dict[str, Any]
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
def modify_token() -> Tuple[Response, int]:
    """
    Revoca el token JWT del usuario que realiza la solicitud, cerrando su sesión.

    Inserta el JTI del token en la tabla `token` de la base de datos para
    marcarlo como revocado.

    Returns
    -------
    Tuple[Response, int]
        Un par (respuesta JSON, código de estado). Si el token se revoca
        exitosamente, se retorna el código 200, o 409 si ya existía en la BD.
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
def add_usuario(identificador: str) -> Tuple[str, int]:
    """
    Añade un nuevo usuario al sistema. Solo los administradores pueden realizar esta acción.

    Lee los datos del usuario (identificador, nombre, apellido1, apellido2, password)
    desde los argumentos de la solicitud (request.args).
    - Si el parámetro `administrador` está en 'si', crea un Administrador
      (solamente el superadministrador, identificador "0", puede hacerlo).
    - En caso contrario, crea un Usuario normal.

    Parameters
    ----------
    identificador : str
        Identificador del usuario a crear.

    Returns
    -------
    Tuple[str, int]
        Un par (mensaje, código de estado). El código puede ser:
        - 200 si el usuario se registra exitosamente.
        - 400 si la contraseña no cumple con los requisitos.
        - 403 si un administrador distinto del superadministrador intenta crear otro administrador.
        - 409 si el usuario ya existe.
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
def update_usuario() -> Tuple[str, int]:
    """
    Actualiza la información de un usuario existente.

    El usuario que realiza la solicitud solo puede actualizar sus propios datos.
    Toma los datos (nombre, apellido1, apellido2) desde los argumentos de la petición.

    Returns
    -------
    Tuple[str, int]
        - 200 si se actualiza correctamente.
        - 404 si el usuario no se encuentra.
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
def get_usuario_actual() -> Tuple[Dict[str, Any], int]:
    """
    Obtiene la información del usuario autenticado.

    Retorna la información del usuario que está realizando la petición,
    convirtiéndola a un diccionario mediante `to_dict()`.

    Returns
    -------
    Tuple[Dict[str, Any], int]
        Un par (diccionario con información del usuario, código 200).
    """
    gu = GestorUsuarios()
    current_user = gu.buscar_usuario(get_jwt_identity())
    return jsonify(current_user.to_dict()), 200


@app.route('/usuario/<string:identificador>', methods=['GET'])
@jwt_required()
def get_usuario(identificador: str) -> Tuple[Union[Dict[str, Any], str], int]:
    """
    Obtiene la información de un usuario específico. Solo los administradores pueden hacerlo.

    Parameters
    ----------
    identificador : str
        Identificador del usuario que se desea consultar.

    Returns
    -------
    Tuple[Union[Dict[str, Any], str], int]
        - 403 si el usuario autenticado no es administrador.
        - 404 si el usuario consultado no existe.
        - 200 y la información del usuario si se encuentra.
    """
    gu = GestorUsuarios()
    current_user = gu.buscar_usuario(get_jwt_identity())

    if not isinstance(current_user, Administrador):
        return 'Solo los administrdores pueden mostrar información de otros usuarios', 403

    u = gu.buscar_usuario(identificador)
    if u:
        return jsonify(u.to_dict()), 200
    else:
        return f'Usuario con identificador {identificador} no encontrado', 404


@app.route('/usuario/<string:identificador>', methods=['DELETE'])
@jwt_required()
def remove_usuario(identificador: str) -> Tuple[str, int]:
    """
    Elimina un usuario del sistema. Solo los administradores pueden realizar esta acción.

    Verifica que el usuario no tenga libros prestados. De lo contrario,
    no se permite eliminarlo.

    Parameters
    ----------
    identificador : str
        Identificador del usuario a eliminar.

    Returns
    -------
    Tuple[str, int]
        - 403 si el usuario autenticado no es administrador.
        - 404 si el usuario no existe.
        - 409 si el usuario tiene préstamos pendientes.
        - 200 si se elimina exitosamente.
    """
    current_id = get_jwt_identity()
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(current_id), Administrador):
        return 'Solo los administradores pueden eliminar usuarios', 403

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


@app.route('/libro/<string:isbn>', methods=['POST'])
@jwt_required()
def add_libro(isbn: str) -> Tuple[str, int]:
    """
    Añade un nuevo libro al sistema. Solo los administradores pueden realizar esta acción.

    Obtiene los datos del libro (titulo, autor, editorial, anyo) desde
    los argumentos de la petición (request.args). Si faltan datos, se intenta
    obtener la información a partir del ISBN llamando a `Libro.por_isbn()`
    (puede fallar si no hay conexión externa).

    Parameters
    ----------
    isbn : str
        ISBN del libro a crear.

    Returns
    -------
    Tuple[str, int]
        - 403 si el usuario autenticado no es administrador.
        - 409 si el libro ya existe.
        - 424 si no se pueden obtener datos externos (falla de conexión).
        - 200 si se crea correctamente.
    """
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden crear libros', 403

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


@app.route('/libro/<string:isbn>', methods=['PUT'])
@jwt_required()
def update_libro(isbn: str) -> Tuple[str, int]:
    """
    Actualiza la información de un libro existente. Solo los administradores pueden hacerlo.

    Si el libro se encuentra prestado, no se permite actualizarlo.
    Los datos (titulo, autor, editorial, anyo) se obtienen de la petición.

    Parameters
    ----------
    isbn : str
        ISBN del libro a actualizar.

    Returns
    -------
    Tuple[str, int]
        - 403 si el usuario autenticado no es administrador.
        - 404 si el libro no existe.
        - 409 si el libro está prestado.
        - 200 si se actualiza correctamente.
    """
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden actualizar libros', 403

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


@app.route('/libro/<string:isbn>', methods=['DELETE'])
@jwt_required()
def remove_libro(isbn: str) -> Tuple[str, int]:
    """
    Elimina un libro del sistema. Solo los administradores pueden realizar esta acción.

    Verifica que el libro no se encuentre prestado antes de eliminarlo.

    Parameters
    ----------
    isbn : str
        ISBN del libro a eliminar.

    Returns
    -------
    Tuple[str, int]
        - 403 si el usuario autenticado no es administrador.
        - 404 si el libro no existe.
        - 409 si el libro está prestado.
        - 200 si se elimina correctamente.
    """
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden eliminar libros', 403

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


@app.route('/libro/<string:isbn>', methods=['GET'])
@jwt_required(optional=True)
def get_libro(isbn: str) -> Tuple[Union[Dict[str, Any], str], int]:
    """
    Obtiene la información de un libro.

    - Si el usuario está autenticado y es administrador, se incluye información
      sobre si el libro está prestado y a qué usuario.
    - Si el usuario no es administrador (o no está autenticado), solo se indica
      si el libro está disponible o no.

    Parameters
    ----------
    isbn : str
        ISBN del libro a consultar.

    Returns
    -------
    Tuple[Union[Dict[str, Any], str], int]
        - 404 si el libro no existe.
        - 200 y un diccionario con la información del libro.
    """
    gl = GestorLibros()
    gp = GestorPrestamos()
    gu = GestorUsuarios()

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


@app.route('/prestamo/<string:isbn>', methods=['POST'])
@jwt_required()
def add_prestamo(isbn: str) -> Tuple[str, int]:
    """
    Añade un nuevo préstamo. Solo los administradores pueden realizar esta acción.

    Obtiene el identificador del usuario desde los argumentos de la solicitud (request.args).
    Si el libro ya está prestado, se responde con un error.

    Parameters
    ----------
    isbn : str
        ISBN del libro que se desea prestar.

    Returns
    -------
    Tuple[str, int]
        - 403 si el usuario autenticado no es administrador.
        - 409 si el libro ya está prestado.
        - 200 si el libro se presta exitosamente.
    """
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden prestar libros', 403

    identificador = request.args.get('identificador')
    gp = GestorPrestamos()

    try:
        gp.add_prestamo(isbn, identificador)
        gp.guardar_prestamos()
        return f'El libro con ISBN {isbn} ha sido prestado al usuario {identificador}', 200
    except LibroNoDisponibleError:
        return f'El libro con ISBN {isbn} ya está prestado al usuario {identificador}', 409


@app.route('/prestamo/<string:isbn>', methods=['DELETE'])
@jwt_required()
def remove_prestamo(isbn: str) -> Tuple[str, int]:
    """
    Elimina (registra la devolución) de un préstamo. Solo los administradores pueden realizar esta acción.

    Se utiliza el identificador del token JWT para verificar quién devuelve el libro.
    Si el préstamo no existe o no corresponde al usuario, se devuelve un error.

    Parameters
    ----------
    isbn : str
        ISBN del libro que se va a devolver.

    Returns
    -------
    Tuple[str, int]
        - 200 si el libro se devuelve correctamente.
        - 403 si el préstamo no pertenece al usuario que hace la solicitud.
        - 404 si el libro no está prestado.
    """
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
def cambiar_password() -> Tuple[str, int]:
    """
    Cambia la contraseña de un usuario autenticado, verificando primero la contraseña antigua.

    La nueva contraseña debe cumplir con los requisitos de complejidad.

    Returns
    -------
    Tuple[str, int]
        - 200 si la contraseña se actualiza correctamente.
        - 400 si la contraseña antigua no coincide o la nueva no cumple requisitos.
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
        usuario_a_actualizar.hashed_password = new_password_hash
        gu.guardar_usuarios()
        return 'Contraseña cambiada correctamente', 200
    else:
        return 'Contraseña antigua incorrecta', 400


@app.route('/caratula/<string:isbn>', methods=['POST'])
@jwt_required()
def subir_caratula(isbn: str) -> Tuple[str, int]:
    """
    Sube la carátula de un libro. Solo los administradores pueden realizar esta acción.

    Recibe el archivo de carátula desde un campo 'file' de tipo multipart/form-data
    y lo guarda en la carpeta configurada en 'app.config["UPLOAD_FOLDER"]'
    con nombre ISBN + extensión original.

    Parameters
    ----------
    isbn : str
        ISBN del libro al que se desea subir la carátula.

    Returns
    -------
    Tuple[str, int]
        - 403 si el usuario autenticado no es administrador.
        - 404 si el libro no existe.
        - 200 si se guarda la carátula exitosamente.
    """
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden subir carátulas', 403

    gl = GestorLibros()
    if not gl.buscar_libro(isbn):
        return f'Libro con ISBN {isbn} no encontrado', 404

    file = request.files['file']
    extension = file.filename.rsplit('.', 1)[-1]
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{isbn}.{extension}"))
    return f'Carátula del libro con ISBN {isbn} guardada', 200


@app.route('/caratula/<string:isbn>', methods=['GET'])
def bajar_caratula(isbn: str) -> Tuple[Union[Response, str], int]:
    """
    Descarga la carátula de un libro, si existe.

    Parameters
    ----------
    isbn : str
        ISBN del libro cuya carátula se desea descargar.

    Returns
    -------
    Tuple[Union[Response, str], int]
        - 404 si no se encuentra el libro o no tiene carátula.
        - 200 y el archivo si se encuentra.
    """
    file = GestorLibros.buscar_caratula(isbn)

    if file is None:
        return f'Libro con ISBN {isbn} no encontrado o sin carátula', 404

    return send_file(file), 200


@app.route('/exportar', methods=['GET'])
def exportar() -> Tuple[Response, int]:
    """
    Exporta los datos de la biblioteca y los comprime en un archivo.

    Llama a la función `exportacion.comprime()` para generar el archivo
    comprimido con los datos (usuarios, libros, préstamos).

    Returns
    -------
    Tuple[Response, int]
        Un par (archivo exportado, código 200).
    """
    return send_file(exportacion.comprime()), 200


@app.route('/carne', methods=['GET'])
@jwt_required()
def bajar_carne() -> Tuple[Response, int]:
    """
    Descarga el carné de un usuario autenticado.

    Genera un carné con la función `generar_carne()`, basándose en la
    información del usuario autenticado.

    Returns
    -------
    Tuple[Response, int]
        Un par (archivo, código 200) con el carné del usuario.
    """
    gu = GestorUsuarios()
    return send_file(generar_carne(gu.buscar_usuario(get_jwt_identity()))), 200


@app.route('/ficha/<string:isbn>', methods=['GET'])
def bajar_ficha(isbn: str) -> Tuple[Union[Response, str], int]:
    """
    Descarga la ficha de un libro (por ejemplo, en formato PDF).

    Se llama a `generar_ficha()` para generar la ficha.

    Parameters
    ----------
    isbn : str
        ISBN del libro cuya ficha se desea descargar.

    Returns
    -------
    Tuple[Union[Response, str], int]
        - 200 y el archivo si se genera correctamente.
        - 404 si no se encuentra el libro.
    """
    gl = GestorLibros()
    l = gl.buscar_libro(isbn)
    if l:
        return send_file(generar_ficha(l)), 200
    else:
        return f'Libro con ISBN {isbn} no encontrado', 404


@app.route('/informe_prestamos', methods=['GET'])
@jwt_required()
def bajar_informe_prestamos() -> Tuple[Union[Response, str], int]:
    """
    Descarga un informe de préstamos en formato PDF u otro formato definido.

    Solo los administradores pueden generar informes de préstamos.
    Se llama a `generar_prestamos()` para generar el archivo.

    Returns
    -------
    Tuple[Union[Response, str], int]
        - 403 si el usuario autenticado no es administrador.
        - 200 y el archivo si se genera correctamente.
    """
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden generar informes de préstamos', 403

    return send_file(generar_prestamos()), 200


@app.route('/referencia/<string:isbn>', methods=['GET'])
def get_referencia(isbn: str) -> Tuple[Union[Dict[str, Any], str], int]:
    """
    Obtiene la referencia de un libro en un formato específico (APA, MLA, etc.).

    El formato se obtiene desde `request.args.get('formato')`. Se llama
    a la función `generar_referencias()` del libro, que retorna un
    diccionario con distintas referencias.

    Parameters
    ----------
    isbn : str
        ISBN del libro cuya referencia se solicita.

    Returns
    -------
    Tuple[Union[Dict[str, Any], str], int]
        - 400 si el formato solicitado no es válido.
        - 404 si el libro no existe.
        - 200 y la referencia solicitada si se genera correctamente.
    """
    gl = GestorLibros()
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
def bajar_log() -> Tuple[Union[Response, str], int]:
    """
    Descarga el fichero de registro (log) de los inicios de sesión del sistema.

    Solo los administradores pueden descargar el log.

    Returns
    -------
    Tuple[Union[Response, str], int]
        - 403 si el usuario no es administrador.
        - 200 y el fichero de log si se tiene permiso.
    """
    gu = GestorUsuarios()
    if not isinstance(gu.buscar_usuario(get_jwt_identity()), Administrador):
        return 'Solo los administradores pueden descargar el log', 403

    return send_file(PATH_LOG), 200


if __name__ == '__main__':
    app.run(debug=True)