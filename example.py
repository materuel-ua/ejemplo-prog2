"""
Script con ejemplos de llamadas a la API RESTful de la biblioteca usando el módulo requests.
Implementa una rudimentaria interfaz textual para interactuar con la aplicación.

Contiene las siguientes funciones:
- param: Solicita un parámetro por consola, validando tipo y longitud mínima.
- main: Muestra el menú para interactuar con la API RESTful.
"""

from typing import Any, Union
import requests
import getpass

URL_remota = 'http://materuel.pythonanywhere.com'
URL_local = 'http://127.0.0.1:5000'

# Elegir la URL a usar según sea local o remota
URL = URL_remota


def param(
    nombre: str,
    tipo: type,
    lon_min: int = 0,
    is_password: bool = False
) -> Any:
    """
    Solicita por consola un valor para la variable `nombre`, validando su longitud mínima y tipo.

    Parameters
    ----------
    nombre : str
        Nombre descriptivo del parámetro (por ejemplo, "Contraseña" o "ISBN").
    tipo : type
        Tipo al que se convertirá la entrada (por ejemplo, str, int).
    lon_min : int, optional
        Longitud mínima permitida para el texto de entrada. Por defecto es 0.
    is_password : bool, optional
        Indica si se debe ocultar la entrada (campo de contraseña). Por defecto es False.

    Returns
    -------
    Any
        El valor convertido al tipo especificado, siempre que cumpla con la longitud mínima.
    """
    valido = False
    out = None
    while not valido:
        prompt = (
            f"{nombre} (Longitud mínima: {lon_min}): "
            if lon_min
            else f"{nombre}: "
        )

        # Si es un campo que se quiere ocultar, usar getpass
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
    Función principal que ejecuta un menú para interactuar con la API RESTful de gestión bibliotecaria.

    Muestra opciones para iniciar/cerrar sesión, gestionar usuarios, libros, préstamos y
    descargar o subir archivos relacionados (carátulas, fichas, informes, etc.).
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
                    f"{URL}/usuario?"
                    f"identificador={param('Identificador', str)}"
                    f"&nombre={param('Nombre', str)}"
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
                    f"{URL}/usuario?identificador={param('Identificador', str)}",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                print(r.text)

            case '6':
                # 6: Buscar usuario
                r = requests.get(
                    f"{URL}/usuario?identificador={param('Identificador', str)}",
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
                    f"{URL}/libro?"
                    f"isbn={param('ISBN', str, lon_min=10)}"
                    f"&titulo={param('Título', str)}"
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
                    f"{URL}/libro?"
                    f"isbn={param('ISBN', str, lon_min=10)}"
                    f"&titulo={param('Título', str)}"
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
                    f"{URL}/libro?isbn={param('ISBN', str, lon_min=10)}",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                print(r.text)

            case '11':
                # 11: Buscar libro
                r = requests.get(
                    f"{URL}/libro?isbn={param('ISBN', str, lon_min=10)}"
                )
                print(r.status_code)
                print(r.text)

            case '12':
                # 12: Subir carátula
                path_caratula = param('Ruta completa al fichero', str)
                with open(path_caratula, 'rb') as file_obj:
                    r = requests.post(
                        f"{URL}/caratula?isbn={param('ISBN', str, lon_min=10)}",
                        headers={'Authorization': 'Bearer ' + (token if token else '')},
                        files={'file': file_obj}
                    )
                print(r.status_code)
                print(r.text)

            case '13':
                # 13: Descargar carátula
                r = requests.get(
                    f"{URL}/caratula?isbn={param('ISBN', str, lon_min=10)}"
                )
                print(r.status_code)
                if r.status_code == 200:
                    with open("caratula.jpg", "wb") as f:
                        f.write(r.content)
                    print("Carátula descargada como 'caratula.jpg'.")

            case '14':
                # 14: Añadir libro por ISBN (sin más datos)
                r = requests.post(
                    f"{URL}/libro?isbn={param('ISBN', str, lon_min=10)}",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                print(r.text)

            case '15':
                # 15: Añadir préstamo
                r = requests.post(
                    f"{URL}/prestamo?"
                    f"isbn={param('ISBN', str, lon_min=10)}"
                    f"&identificador={param('Identificador', str)}",
                    headers={'Authorization': 'Bearer ' + (token if token else '')}
                )
                print(r.status_code)
                print(r.text)

            case '16':
                # 16: Devolver libro
                r = requests.delete(
                    f"{URL}/prestamo?isbn={param('ISBN', str, lon_min=10)}",
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
                    f"{URL}/ficha?isbn={param('ISBN', str, lon_min=10)}"
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
                    f"{URL}/referencia?"
                    f"isbn={param('ISBN', str, lon_min=10)}"
                    f"&formato={fmt}"
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

            case '0':
                # Salir
                print("Saliendo de la aplicación...")

            case _:
                print("Opción no válida. Intente de nuevo.")


if __name__ == "__main__":
    main()