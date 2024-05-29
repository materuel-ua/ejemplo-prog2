import os

import requests

URL = 'http://127.0.0.1:5000/'

# Login superadmin
r = requests.get(f'{URL}/login?identificador=0&password=UAgCZ646D5l9Vbl')
print(r.status_code)
token = r.text
print(token)

# Crear usuario
r = requests.post(f'{URL}/usuario?identificador=12345&nombre=Miguel&apellido1=Teruel&apellido2=Martinez&password=zCWlAusK*7BfFy', headers={'Authorization': 'Bearer ' + token})
print(r.status_code)
print(r.text)

# Buscar usuario
r = requests.get(f'{URL}/usuario?identificador=12345', headers={'Authorization': 'Bearer ' + token})
print(r.status_code)
print(r.text)

# Crear libro
r = requests.post(f'{URL}/libro?isbn=9781492056355&titulo=Fluent Python 2nd Edition&autor=Ramalho, Luciano&editorial=O\'Reilly Media, Inc.&anyo=2022', headers={'Authorization': 'Bearer ' + token})
print(r.status_code)
print(r.text)

# Buscar libro
r = requests.get(f'{URL}/libro?isbn=9781492056355')
print(r.status_code)
print(r.text)

# Buscar libro
r = requests.get(f'{URL}/libro?isbn=9781492056355',  headers={'Authorization': 'Bearer ' + token})
print(r.status_code)
print(r.text)

# Crear préstamo
r = requests.post(f'{URL}/prestamo?isbn=9781492056355&identificador=12345', headers={'Authorization': 'Bearer ' + token})
print(r.status_code)
print(r.text)

# Login usuario
r = requests.get(f'{URL}/login?identificador=12345&password=zCWlAusK*7BfFy')
print(r.status_code)
token_usuario = r.text
print(token)

# Devolver libro
r = requests.delete(f'{URL}/prestamo?isbn=9781492056355', headers={'Authorization': 'Bearer ' + token_usuario})
print(r.status_code)
print(r.text)

# Actualizar libro
r = requests.put(f'{URL}/libro?isbn=9781492056355&titulo=Fluent Python 3rd Edition&autor=Ramalho, Luciano&editorial=O\'Reilly Media, Inc.&anyo=2022', headers={'Authorization': 'Bearer ' + token})
print(r.status_code)
print(r.text)

# Eliminar libro
r = requests.delete(f'{URL}/libro?isbn=9781492056355', headers={'Authorization': 'Bearer ' + token})
print(r.status_code)
print(r.text)

# Actualizar usuario
r = requests.put(f'{URL}/usuario?&nombre=Miguel Angel&apellido1=Teruel&apellido2=Martinez', headers={'Authorization': 'Bearer ' + token_usuario})
print(r.status_code)
print(r.text)

# Eliminar usuario
r = requests.delete(f'{URL}/usuario?identificador=12345', headers={'Authorization': 'Bearer ' + token})
print(r.status_code)
print(r.text)