import json
import multiprocessing
import os.path
import tempfile
import zipfile
import csv

try:
    import zlib

    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

modes = {zipfile.ZIP_DEFLATED: 'deflated',
         zipfile.ZIP_STORED: 'stored',
         }

from gestion_libros.gestor_libros import GestorLibros


def to_json(temp_dir):
    gl = GestorLibros()
    gl.cargar_libros()
    with open(os.path.join(temp_dir, 'biblioteca.json'), 'w') as f:
        f.write(json.dumps([l.to_dict() for l in gl], indent=2))


def to_xml(temp_dir):
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


def to_csv(temp_dir):
    gl = GestorLibros()
    gl.cargar_libros()

    with open(os.path.join(temp_dir, 'biblioteca.csv'), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['isbn', 'autor', 'editorial', 'anyo'])
        for l in gl:
            writer.writerow([l.isbn, l.autor, l.editorial, l.anyo])


def to_bibtex(temp_dir):
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


def comprime():
    funciones = [to_json, to_xml, to_csv, to_bibtex]

    procesos = []

    temp_dir = tempfile.gettempdir()

    for f in funciones:
        p = multiprocessing.Process(target=f, args=(temp_dir,))
        procesos.append(p)
        p.start()

    for p in procesos:
        p.join()

    zip_file = os.path.join(temp_dir, 'biblioteca.zip')

    types = ['json', 'xml', 'csv', 'bib']

    for t in types:
        with zipfile.ZipFile(zip_file, mode="w") as archive:
            print(
                archive.write(os.path.join(temp_dir, f'biblioteca.{t}'), f'biblioteca.{t}', compress_type=compression))

    return zip_file
