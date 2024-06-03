import json
import multiprocessing
import os.path
import tempfile
import zipfile
import csv
from datetime import datetime

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
    funciones = [to_json, to_xml, to_bibtex, to_csv]

    procesos = []

    temp_dir = tempfile.gettempdir()

    for f in funciones:
        p = multiprocessing.Process(target=f, args=(temp_dir,))
        procesos.append(p)
        p.start()

    for p in procesos:
        p.join()

    zip_file = os.path.join(temp_dir, datetime.now().strftime('%y%m%d_%H%M%S')+'.zip')

    with zipfile.ZipFile(zip_file, mode="w") as archive:
        archive.write(os.path.join(temp_dir, f'biblioteca.json'), f'biblioteca.json', compress_type=compression)
        archive.write(os.path.join(temp_dir, f'biblioteca.xml'), f'biblioteca.xml', compress_type=compression)
        archive.write(os.path.join(temp_dir, f'biblioteca.csv'), f'biblioteca.cvs', compress_type=compression)
        archive.write(os.path.join(temp_dir, f'biblioteca.bib'), f'biblioteca.bib', compress_type=compression)

    return zip_file
