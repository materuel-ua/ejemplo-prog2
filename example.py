"""
Script con ejemplos de llamadas a la API RESTful de la biblioteca usando el módulo requests.

Implementa una rudimentaria interfaz textual para interactuar con la aplicación.

Contiene las siguientes funciones:
- param: Solicita un parámetro por consola, validando tipo y longitud mínima.
- main: Muestra un menú para interactuar con la API RESTful.
"""

import json
from typing import Any, Union
import requests
import getpass

try:
    URL = json.load(open('config.json'))['URL']
except FileNotFoundError:
    print('Fichero de configuración no encontrado')
    exit(1)


def param(
    nombre: str,
    tipo: type,
    lon_min: int = 0,
    is_password: bool = False
) -> Any:
    """
    Solicita un valor por consola para la variable indicada, validando su tipo y longitud mínima.

    Parameters
    ----------
    nombre : str
        Nombre descriptivo del parámetro (p. ej., "Contraseña" o "ISBN").
    tipo : type
        Tipo al que se desea convertir la entrada (p. ej., str, int).
    lon_min : int, optional
        Longitud mínima permitida para el texto de entrada. Por defecto, 0.
    is_password : bool, optional
        Indica si se debe ocultar la entrada por consola (campo de contraseña). Por defecto, False.

    Returns
    -------
    Any
        El valor convertido al tipo especificado y que cumple con la longitud mínima.
    """
    valido = False
    out = None
    while not valido:
        prompt = (
            f"{nombre} (Longitud mínima: {lon_min}): "
            if lon_min
            else f"{nombre}: "
        )

        # Oculta la entrada si es un campo de contraseña
        entrada = getpass.getpass(prompt) if is_password else input(prompt)

        if len(entrada) < lon_min:
            print(f"Longitud menor que la requerida: {lon_min}")
        else:
            try:
                out = tipo(entrada)
                valido = True
            except (ValueError, TypeError):
                print("El tipo de dato no es válido.")

    return out


def main() -> None:
    """
    Ejecuta un menú en consola para interactuar con la API RESTful de gestión bibliotecaria.

    Ofrece opciones para iniciar/cerrar sesión, gestionar usuarios, libros y préstamos,
    así como subir/descargar distintos archivos relacionados (carátulas, fichas, informes, etc.).

    Returns
    -------
    None
        Esta función no devuelve ningún valor.
    """
    opcion: str = ''
    token: Union[str, None] = None

    while opcion != '0':
        print("======= MENÚ PRINCIPAL =======")
        print("1:  Iniciar sesión")
        print("2:  Cerrar sesión")
        print("3:  Crear usuario")
        print("4:  Actualizar usuario")
        print("5:  Eliminar usuario")
        print("6:  Buscar usuario")
        print("7:  Cambiar contraseña")
        print("8:  Añadir libro")
        print("9:  Actualizar libro")
        print("10: Eliminar libro")
        print("11: Buscar libro")
        print("12: Subir carátula")
        print("13: Descargar carátula")
        print("14: Añadir libro por ISBN (con búsqueda de datos externa)")
        print("15: Añadir préstamo")
        print("16: Devolver libro")
        print("17: Generar informe de préstamos")
        print("18: Exportar biblioteca")
        print("19: Generar carné de usuario")
        print("20: Generar ficha de libro")
        print("21: Generar referencia del libro")
        print("22: Descarga registro de inicios de sesión")
        print("23: Mostrar usuario actual")
        print("0:  Salir")
        opcion = input("Opción: ")

        match opcion:
            case '1':
                # 1: Iniciar sesión
                r = requests.get(
                    f"{URL}/login?identificador={param('Identificador', str)}"
                    f"&password={param('Contraseña', str, is_password=True)}"
                )
                print(r.status_code)
                token = r.text  # Guardamos el token si la autenticación fue correcta
                print(token)

            case '2':
                # 2: Cerrar sesión
                if token is None:
                    print("No hay sesión iniciada.")
                else:
                    r = requests.delete(
                        f"{URL}/logout",
                        headers={'Authorization': 'Bearer ' + token}
                    )
                    print(r.status_code)
                    print(r.text)
                    token = None

            case '3':
                # 3: Crear usuario
                r = requests.post(
                    f"{URL}/usuario/{param('Identificador', str)}?"
                    f"nombre={param('Nombre', str)}"
                    f"&apellido1={param('Apellido 1', str)}"
                    f"&apellido2={param('Apellido 2', str)}"
                    f"&password={param('Contraseña', str, is_password=True)}",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                print(r.text)

            case '4':
                # 4: Actualizar usuario
                r = requests.put(
                    f"{URL}/usuario?"
                    f"nombre={param('Nombre', str)}"
                    f"&apellido1={param('Apellido 1', str)}"
                    f"&apellido2={param('Apellido 2', str)}",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                print(r.text)

            case '5':
                # 5: Eliminar usuario
                r = requests.delete(
                    f"{URL}/usuario/{param('Identificador', str)}",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                print(r.text)

            case '6':
                # 6: Buscar usuario
                r = requests.get(
                    f"{URL}/usuario/{param('Identificador', str)}",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                print(r.text)

            case '7':
                # 7: Cambiar contraseña
                r = requests.put(
                    f"{URL}/cambiar_password?"
                    f"old_password={param('Contraseña actual', str, is_password=True)}"
                    f"&new_password={param('Nueva contraseña', str, is_password=True)}",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                print(r.text)

            case '8':
                # 8: Añadir libro
                r = requests.post(
                    f"{URL}/libro/{param('ISBN', str, lon_min=10)}?"
                    f"titulo={param('Título', str)}"
                    f"&autor={param('Autor', str)}"
                    f"&editorial={param('Editorial', str)}"
                    f"&anyo={param('Año', str)}",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                print(r.text)

            case '9':
                # 9: Actualizar libro
                r = requests.put(
                    f"{URL}/libro/{param('ISBN', str, lon_min=10)}?"
                    f"titulo={param('Título', str)}"
                    f"&autor={param('Autor', str)}"
                    f"&editorial={param('Editorial', str)}"
                    f"&anyo={param('Año (por ejemplo, 2022)', str)}",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                print(r.text)

            case '10':
                # 10: Eliminar libro
                r = requests.delete(
                    f"{URL}/libro/{param('ISBN', str, lon_min=10)}",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                print(r.text)

            case '11':
                # 11: Buscar libro
                r = requests.get(
                    f"{URL}/libro/{param('ISBN', str, lon_min=10)}"
                )
                print(r.status_code)
                print(r.text)

            case '12':
                # 12: Subir carátula
                path_caratula = param('Ruta completa al fichero', str)
                with open(path_caratula, 'rb') as file_obj:
                    r = requests.post(
                        f"{URL}/caratula/{param('ISBN', str, lon_min=10)}",
                        headers={'Authorization': 'Bearer ' + (token if token else '')},
                        files={'file': file_obj}
                    )
                print(r.status_code)
                print(r.text)

            case '13':
                # 13: Descargar carátula
                r = requests.get(
                    f"{URL}/caratula/{param('ISBN', str, lon_min=10)}"
                )
                print(r.status_code)
                if r.status_code == 200:
                    with open("caratula.jpg", "wb") as f:
                        f.write(r.content)
                    print("Carátula descargada como 'caratula.jpg'.")

            case '14':
                # 14: Añadir libro por ISBN (sin más datos)
                r = requests.post(
                    f"{URL}/libro/{param('ISBN', str, lon_min=10)}",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                print(r.text)

            case '15':
                # 15: Añadir préstamo
                r = requests.post(
                    f"{URL}/prestamo/{param('ISBN', str, lon_min=10)}?"
                    f"identificador={param('Identificador', str)}",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                print(r.text)

            case '16':
                # 16: Devolver libro
                r = requests.delete(
                    f"{URL}/prestamo/{param('ISBN', str, lon_min=10)}",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                print(r.text)

            case '17':
                # 17: Generar informe de préstamos
                r = requests.get(
                    f"{URL}/informe_prestamos",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                if r.status_code == 200:
                    with open("prestamos.pdf", "wb") as f:
                        f.write(r.content)
                    print("Informe de préstamos descargado como 'prestamos.pdf'.")

            case '18':
                # 18: Exportar biblioteca
                r = requests.get(f"{URL}/exportar")
                print(r.status_code)
                if r.status_code == 200:
                    with open("biblioteca.zip", "wb") as f:
                        f.write(r.content)
                    print("Datos de la biblioteca exportados como 'biblioteca.zip'.")

            case '19':
                # 19: Generar carné de usuario
                r = requests.get(
                    f"{URL}/carne",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                if r.status_code == 200:
                    with open("carne.pdf", "wb") as f:
                        f.write(r.content)
                    print("Carné descargado como 'carne.pdf'.")

            case '20':
                # 20: Generar ficha de libro
                r = requests.get(
                    f"{URL}/ficha/{param('ISBN', str, lon_min=10)}"
                )
                print(r.status_code)
                if r.status_code == 200:
                    with open("ficha.pdf", "wb") as f:
                        f.write(r.content)
                    print("Ficha del libro descargada como 'ficha.pdf'.")

            case '21':
                # 21: Generar referencia del libro
                fmt = param("Formato (APA, MLA, Chicago, Turabian, IEEE)", str)
                r = requests.get(
                    f"{URL}/referencia/{param('ISBN', str, lon_min=10)}"
                    f"?formato={fmt}"
                )
                print(r.status_code)
                print(r.text)

            case '22':
                # 22: Descarga registro de inicios de sesión
                r = requests.get(
                    f"{URL}/log", headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                if r.status_code == 200:
                    with open("login.log", "wb") as f:
                        f.write(r.content)
                    print('Inicios de sesión descargados como "login.log".')

            case '23':
                # 23: Mostrar usuario actual
                r = requests.get(
                    f"{URL}/usuario", headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                print(r.text)

            case '0':
                # Salir
                print("Saliendo de la aplicación...")

            case _:
                print("Opción no válida. Intente de nuevo.")


if __name__ == "__main__":
    main()