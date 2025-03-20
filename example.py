"""
Script con ejemplos de llamadas a la API RESTful de la biblioteca usando el módulo requests. Implementa una
rudimentaria interfaz textual.

Contiene las siguientes funciones:

    * main - muestra el menú para interactuar con la API RESTful

"""
from typing import Any

import requests
import getpass

URL_remota = 'http://miji.pythonanywhere.com'
URL_local = 'http://127.0.0.1:5000'

URL = URL_local


def param(nombre, tipo, lon_min=0, is_password=False):
    valido = False
    out = None
    while not valido:

        prompt = f'{nombre}{' (Longitud mínima:' + str(lon_min) + '):' if lon_min else ':'}'

        out = getpass.getpass(prompt) if is_password else input(prompt)

        if lon_min > len(out):
            print('Longitud menor que la requerida')
        else:
            try:
                out = tipo(out)
                valido = True
            except TypeError:
                print('El tipo de dato no es valido')
    return out


def main() -> None:
    """
    Función principal que ejecuta un menú para interactuar con una API RESTful de gestión bibliotecaria.

    Returns
    -------
    None
    """
    opcion: str = ''
    token: Any[str, None] = ''

    while opcion != '0':
        print('1: Login')
        print('2: Nuevo usuario')
        print('3: Buscar usuario')
        print('4: Nuevo libro')
        print('5: Buscar libro')
        print('6: Nuevo préstamo')
        print('7: Logout')
        print('8: Devolver libro')
        print('9: Actualizar libro')
        print('10: Eliminar libro')
        print('11: Actualizar usuario')
        print('12: Cambiar contraseña')
        print('13: Eliminar usuario')
        print('14: Subir carátula')
        print('15: Bajar carátula')
        print('16: Añadir libro por ISBN')
        print('17: Exportar biblioteca')
        print('18: Generar carné')
        print('19: Generar ficha libro')
        print('20: Generar informe de préstamos')
        print('21: Generar referencia de libro')

        opcion = input('Opción: ')
        match opcion:
            case '1':
                # Login
                r = requests.get(
                    f'{URL}/login?identificador={param('Identificador', str)}&password={param('Contraseña', str, is_password=True)}')
                print(r.status_code)
                token = r.text
                print(token)

            case '2':
                # Crear usuario
                r = requests.post(
                    f'{URL}/usuario?identificador={param('Identificador', str)}&nombre={param('Nombre', str)}&apellido1={param('Apellido 1', str)}&apellido2={param('Apellido 2', str)}&password={param('Contraseña', str, is_password=True)}',
                    headers={'Authorization': 'Bearer ' + token})
                print(r.status_code)
                print(r.text)

            case '3':
                # Buscar usuario
                r = requests.get(f'{URL}/usuario?identificador={param('Identificador', str)}', headers={'Authorization': 'Bearer ' + token})
                print(r.status_code)
                print(r.text)

            case '4':
                # Crear libro
                r = requests.post(
                    f'{URL}/libro?isbn={param('ISBN', str, lon_min=10)}&titulo={param('Título', str)}&autor={param('Autor', str)}&editorial={param('Editorial', str)}&anyo={param('Año', str)}',
                    headers={'Authorization': 'Bearer ' + token})
                print(r.status_code)
                print(r.text)

            case '5':
                # Buscar libro
                r = requests.get(f'{URL}/libro?isbn={param('ISBN', str, lon_min=10)}')
                print(r.status_code)
                print(r.text)

            case '6':
                # Crear préstamo
                r = requests.post(f'{URL}/prestamo?isbn={param('ISBN', str, lon_min=10)}&identificador={param('Identificador', str)}',
                                  headers={'Authorization': 'Bearer ' + token})
                print(r.status_code)
                print(r.text)

            case '7':
                # Logout usuario
                r = requests.delete(f'{URL}/logout',
                                 headers={'Authorization': 'Bearer ' + token})
                print(r.status_code)
                print(r.text)
                token = None

            case '8':
                # Devolver libro
                r = requests.delete(f'{URL}/prestamo?isbn={param('ISBN', str, lon_min=10)}',
                                    headers={'Authorization': 'Bearer ' + token})
                print(r.status_code)
                print(r.text)

            case '9':
                # Actualizar libro
                r = requests.put(
                    f'{URL}/libro?isbn={param('ISBN', str, lon_min=10)}&titulo={param('Título', str)}&autor={param('Autor', str)}&editorial={param('Editorial', str)}&anyo=2022',
                    headers={'Authorization': 'Bearer ' + token})
                print(r.status_code)
                print(r.text)

            case '10':
                # Eliminar libro
                r = requests.delete(f'{URL}/libro?isbn={param('ISBN', str, lon_min=10)}', headers={'Authorization': 'Bearer ' + token})
                print(r.status_code)
                print(r.text)

            case '11':
                # Actualizar usuario
                r = requests.put(f'{URL}/usuario?&nombre={param('Nombre', str)}&apellido1={param('Apellido 1', str)}&apellido2={param('Apellido 2', str)}',
                                 headers={'Authorization': 'Bearer ' + token})
                print(r.status_code)
                print(r.text)

            case '12':
                # Cambiar contraseña
                r = requests.put(f'{URL}/cambiar_password?old_password={param('Contraseña actual', str, is_password=True)}&new_password={param('Nueva contraseña', str, is_password=True)}',
                                 headers={'Authorization': 'Bearer ' + token})
                print(r.status_code)
                print(r.text)

            case '13':
                # Eliminar usuario
                r = requests.delete(f'{URL}/usuario?identificador={param('Identificador', str)}', headers={'Authorization': 'Bearer ' + token})
                print(r.status_code)
                print(r.text)

            case '14':
                # Subir carátula
                r = requests.post(f'{URL}/caratula?isbn={param('ISBN', str, lon_min=10)}', headers={'Authorization': 'Bearer ' + token},
                                  files={'file': open(f'{param('Ruta completa al fichero)', str)}', 'rb')})
                print(r.status_code)
                print(r.text)

            case '15':
                # Bajar carátula
                r = requests.get(f'{URL}/caratula?isbn={param('ISBN', str, lon_min=10)}')
                print(r.status_code)
                if r.status_code == 200:
                    open("caratula.jpg", "wb").write(r.content)

            case '16':
                # Añadir libro por ISBN
                r = requests.post(f'{URL}/libro?isbn={param('ISBN', str, lon_min=10)}', headers={'Authorization': 'Bearer ' + token})
                print(r.status_code)
                print(r.text)

            case '17':
                # Exportar biblioteca
                r = requests.get(f'{URL}/exportar')
                print(r.status_code)
                if r.status_code == 200:
                    open("biblioteca.zip", "wb").write(r.content)

            case '18':
                # Generar carné
                r = requests.get(f'{URL}/carne', headers={'Authorization': 'Bearer ' + token})
                print(r.status_code)
                if r.status_code == 200:
                    open("carne.pdf", "wb").write(r.content)

            case '19':
                # Generar ficha
                r = requests.get(f'{URL}/ficha?isbn={param('ISBN', str, lon_min=10)}')
                print(r.status_code)
                if r.status_code == 200:
                    open("ficha.pdf", "wb").write(r.content)

            case '20':
                # Generar informe préstamos
                r = requests.get(f'{URL}/informe_prestamos', headers={'Authorization': 'Bearer ' + token})
                print(r.status_code)
                if r.status_code == 200:
                    open("prestamos.pdf", "wb").write(r.content)

            case '21':
                # Generar referencia
                r = requests.get(f'{URL}/referencia?isbn={param('ISBN', str, lon_min=10)}&formato={param('Formato (APA, MLA, Chicago, Turabian, IEEE)', str)}')
                print(r.status_code)
                print(r.text)


if __name__ == "__main__":
    main()
