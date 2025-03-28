# Gestión de biblioteca

Proyecto de ejemplo de la asignatura Programación 2 (GIA) consistente en la gestión de una biblioteca.

## Autores
* Apellido 1, Apellido 1, Nombre 1
* Apellido 2, Apellido 2, Nombre 2
* Apellido 3, Apellido 3, Nombre 3
* Apellido 4, Apellido 4, Nombre 4
* Apellido 5, Apellido 5, Nombre 5

## Requisitos

* Permitirá la gestión de libros, usuarios (alta, baja, modificación, acceso) y roles del sistema (usuarios estándar y administradores) (Alumno 1)
* Guardará información de usuarios y libros en disco (Alumno 1)
* El catálogo de libros se podrá importar y exportar en formatos JSON, CSV, XML y BibTeX (Alumno 2)
* Permitirá la exportación de citas bibliográficas de los libros en formato APA, MLA, Chicago, Turabian e IEEE (Alumno 2)
* Tendrá una API RESTful que permitirá el uso de la aplicación (Alumno 3)
* Almacenará las carátulas de los libros en formato PNG (Alumno 3)
* Expondrá una API de consulta de libros actuales (Alumno 4)
* Usará la API de Google Books para obtener información sobre un libro en base a su ISBN (Alumno 4)
* Exportará carnés de usuarios y fichas de libros en formato PDF (Alumno 5)
* Emitirá informes en formato PDF de los libros actualmente en préstamo (Alumno 5)
* Guardará un registro de todos los usuarios que inicien sesión en el sistema (Alumno 5)

## Instrucciones de instalación y ejecución
* Editar las rutas en el fichero de configuración _config.py_
* Establecer passwords de Flask y super-administrador en el fichero de configuración _config.py_
* Ejecutar script _init.py_
* Crear venv con el fichero _requirements.txt_
* Ejecutar app Flask desde _main.py_
* (opcional) Probar usando _example.py_ tras modificar adecuadamente _config.json_, mientras se mantiene _main.py_ en ejecución.
* (opcional) Generar ejecutable del cliente usando _build.sh_

## Posibles mejoras

* Comprobar los parámetros de entrada de las peticiones a la API
* Posibilidad de que un libro tenga más de un autor
* Permitir más tipos de publicaciones además de libros (artículos científicos, actas de congresos, informes, etc.)
* Controlar paginación en informe de préstamos en PDF y mejorar maquetación
* Sustituir almacenamiento en ficheros binarios por base de datos SQL / NoSQL

## Resumen de la API

### Autenticación
* Login
  * GET /login
  * Parámetros: identificador, password

* Logout
  * DELETE /logout
  * Requiere JWT

### Gestión de Usuarios
* Añadir un usuario
  * POST /usuario/identificador
  * Requiere JWT (Administrador)
  * Parámetros: nombre, apellido1, apellido2, password, administrador
* Actualizar usuario
  * PUT /usuario
  * Requiere JWT
  * Parámetros: nombre, apellido1, apellido2
* Obtener información un usuario
  * GET /usuario/identificador
  * Requiere JWT
  * Parámetros:  (opcional)
* Obtener información del usuario actual
  * GET /usuario
  * Requiere JWT
* Eliminar un usuario
  * DELETE /usuario/identificador
  * Requiere JWT (Administrador)
* Cambiar contraseña
  * PUT /cambiar_password
  * Requiere JWT
  * Parámetros: old_password, new_password

### Gestión de Libros
* Añadir un libro
  * POST /libro/isbn
  * Requiere JWT (Administrador)
  * Parámetros: titulo, autor, editorial, anyo
* Actualizar un libro
  * PUT /libro/isbn
  * Requiere JWT (Administrador)
  * Parámetros: titulo, autor, editorial, anyo
* Obtener información de un libro
  * GET /libro/isbn
  * Requiere JWT (opcional)
* Eliminar un libro
  * DELETE /libro/isbn
  * Requiere JWT (Administrador)
* Subir carátula de un libro
  * POST /caratula/sibn
  * Requiere JWT (Administrador)
  * Parámetros: Archivo en form-data
* Descargar carátula de un libro
  * GET /caratula/isbn

### Gestión de Préstamos
* Añadir un préstamo
  * POST /prestamo/isbn
  * Requiere JWT (Administrador)
  * Parámetros: identificador
* Eliminar un préstamo
  * DELETE /prestamo/isbn
  * Requiere JWT

### Informes y Exportación
* Exportar datos de la biblioteca
  * GET /exportar
* Descargar carné de usuario
  * GET /carne
  * Requiere JWT
* Descargar ficha de libro
  * GET /ficha/isbn
* Descargar informe de préstamos
  * GET /informe_prestamos
  * Requiere JWT (Administrador)
* Obtener referencia de un libro
  * GET /referencia/isbn
  * Parámetros: formato
* Descargar registro de inicios de sesión
  * GET /log
  * Requiere JWT (Administrador)
