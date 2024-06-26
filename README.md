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

## Instrucciones de instalación y ejecución
* Editar las rutas en el fichero de configuración _config.py_
* Establecer passwords de Flask y super-administrador en el fichero de configuración _config.py_
* Ejecutar script _init.py_
* Crear venv con el fichero _requirements.txt_
* Ejecutar app Flask desde _main.py_
* (opcional) Probar usando_example.py_ tras modificarlo adecuadamente, mientras se mantiene _main.py_ en ejecución.

## Posibles mejoras

* Comprobar los parámetros de entrada de las peticiones a la API
* Posibilidad de que un libro tenga más de un autor
* Permitir más tipos de publicaciones además de libros (artículos científicos, actas de congresos, informes, etc.)
* Controlar paginación en informe de préstamos en PDF y mejorar maquetación
* Sustituir almacenamiento en ficheros binarios por base de datos SQL / NoSQL
