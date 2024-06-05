"""
Módulo para la exportación de una colección de libros en varios formatos y compresión en un archivo ZIP.

Este módulo proporciona funciones para exportar los datos de una colección de libros en formatos JSON, XML, CSV y BibTeX,
y luego comprime estos archivos en un archivo ZIP. Utiliza multiprocesamiento para realizar las exportaciones en paralelo.

Funciones:
    - to_json(temp_dir: str) -> None: Exporta los libros a un archivo JSON.
    - to_xml(temp_dir: str) -> None: Exporta los libros a un archivo XML.
    - to_csv(temp_dir: str) -> None: Exporta los libros a un archivo CSV.
    - to_bibtex(temp_dir: str) -> None: Exporta los libros a un archivo BibTeX.
    - comprime() -> str: Comprime los archivos exportados en un archivo ZIP y retorna la ruta del archivo ZIP.
"""

import json
import multiprocessing
import os.path
import tempfile
import zipfile
import csv
from datetime import datetime
from typing import List

try:
    import zlib

    compression = zipfile.ZIP_DEFLATED
except ImportError:
    compression = zipfile.ZIP_STORED

modes = {zipfile.ZIP_DEFLATED: 'deflated',
         zipfile.ZIP_STORED: 'stored',
         }

from gestion_libros.gestor_libros import GestorLibros


def to_json(temp_dir: str) -> None:
    """
    Exporta los libros a un archivo JSON.

    Parámetros:
    -----------
    temp_dir : str
        Directorio temporal donde se guardará el archivo JSON.
    """
    gl = GestorLibros()
    gl.cargar_libros()
    with open(os.path.join(temp_dir, 'biblioteca.json'), 'w') as f:
        f.write(json.dumps([l.to_dict() for l in gl], indent=2))


def to_xml(temp_dir: str) -> None:
    """
    Exporta los libros a un archivo XML.

    Parámetros:
    -----------
    temp_dir : str
        Directorio temporal donde se guardará el archivo XML.
    """
    output = '<biblioteca>\n'
    gl = GestorLibros()
    gl.cargar_libros()

    for l in gl:
        output += '\t<libro>\n'
        output += f'\t\t<isbn>{l.isbn}</isbn>\n'
        output += f'\t\t<autor>{l.autor}</autor>\n'
        output += f'\t\t<editorial>{l.editorial}</editorial>\n'
        output += f'\t\t<anyo>{l.anyo}</anyo>\n'
        output += '\t</libro>\n'
    output += '</biblioteca>'

    with open(os.path.join(temp_dir, 'biblioteca.xml'), 'w') as f:
        f.write(output)


def to_csv(temp_dir: str) -> None:
    """
    Exporta los libros a un archivo CSV.

    Parámetros:
    -----------
    temp_dir : str
        Directorio temporal donde se guardará el archivo CSV.
    """
    gl = GestorLibros()
    gl.cargar_libros()

    with open(os.path.join(temp_dir, 'biblioteca.csv'), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['isbn', 'autor', 'editorial', 'anyo'])
        for l in gl:
            writer.writerow([l.isbn, l.autor, l.editorial, l.anyo])


def to_bibtex(temp_dir: str) -> None:
    """
    Exporta los libros a un archivo BibTeX.

    Parámetros:
    -----------
    temp_dir : str
        Directorio temporal donde se guardará el archivo BibTeX.
    """
    output = ''
    gl = GestorLibros()
    gl.cargar_libros()

    for i in range(len(gl)):
        output += f'@book{{libro{i + 1},\n'
        output += f'\ttitle="{gl[i].titulo}",\n'
        output += f'\tautor="{gl[i].autor}",\n'
        output += f'\tyear={gl[i].anyo},\n'
        output += f'\tpublisher="{gl[i].editorial}",\n'
        output += f'\tisbn="{gl[i].isbn}"\n'
        output += '}\n'

    with open(os.path.join(temp_dir, 'biblioteca.bib'), 'w') as f:
        f.write(output)


def comprime() -> str:
    """
    Comprimes los archivos exportados en un archivo ZIP y retorna la ruta del archivo ZIP.

    Retorna:
    --------
    str
        Ruta del archivo ZIP generado.
    """
    funciones = [to_json, to_xml, to_bibtex, to_csv]
    procesos: List[multiprocessing.Process] = []

    temp_dir = tempfile.gettempdir()

    # Ejecuta las funciones de exportación en paralelo
    for f in funciones:
        p = multiprocessing.Process(target=f, args=(temp_dir,))
        procesos.append(p)
        p.start()

    for p in procesos:
        p.join()

    # Nombre del archivo ZIP basado en la fecha y hora actuales
    zip_file = os.path.join(temp_dir, datetime.now().strftime('%y%m%d_%H%M%S') + '.zip')

    # Comprime los archivos exportados en un archivo ZIP
    with zipfile.ZipFile(zip_file, mode="w") as archive:
        archive.write(os.path.join(temp_dir, 'biblioteca.json'), 'biblioteca.json', compress_type=compression)
        archive.write(os.path.join(temp_dir, 'biblioteca.xml'), 'biblioteca.xml', compress_type=compression)
        archive.write(os.path.join(temp_dir, 'biblioteca.csv'), 'biblioteca.csv', compress_type=compression)
        archive.write(os.path.join(temp_dir, 'biblioteca.bib'), 'biblioteca.bib', compress_type=compression)

    return zip_file
