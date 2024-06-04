"""
Módulo para la generación de documentos PDF relacionados con la gestión de usuarios, libros y préstamos.

Este módulo proporciona funciones para generar carnés de usuario, fichas de libros y listados de préstamos en formato PDF.

Funciones:
    - generar_carne(usuario) -> str: Genera un carné de usuario en formato PDF.
    - generar_ficha(libro) -> str: Genera una ficha de libro en formato PDF.
    - generar_prestamos() -> str: Genera un listado de préstamos en formato PDF.
"""

import os
import tempfile
from datetime import datetime

from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table

from gestion_libros.gestor_libros import GestorLibros
from gestion_prestamos.gestor_prestamos import GestorPrestamos
from gestion_usuarios.gestor_usuarios import GestorUsuarios


def generar_carne(usuario) -> str:
    """
    Genera un carné de usuario en formato PDF.

    Parámetros:
    -----------
    usuario : Usuario
        Instancia de la clase Usuario para el cual se generará el carné.

    Retorna:
    --------
    str
        Ruta del archivo PDF generado.
    """
    filename = os.path.join(tempfile.gettempdir(), f'carne_{usuario.identificador}.pdf')
    canvas = Canvas(filename, pagesize=(8 * cm, 5 * cm))
    canvas.setFont('Helvetica', 12)
    canvas.drawCentredString(4 * cm, 4.5 * cm, 'Carné de Usuario')
    canvas.setFont('Helvetica-Bold', 8)
    canvas.drawString(1 * cm, 4 * cm, 'Número de socio: ')
    canvas.drawString(1 * cm, 3 * cm, 'Nombre: ')
    canvas.drawString(1 * cm, 2 * cm, 'Primer apellido: ')
    canvas.drawString(1 * cm, 1 * cm, 'Segundo apellido: ')
    canvas.setFont('Helvetica', 8)
    canvas.drawString(1 * cm, 3.5 * cm, usuario.identificador)
    canvas.drawString(1 * cm, 2.5 * cm, usuario.nombre)
    canvas.drawString(1 * cm, 1.5 * cm, usuario.apellido1)
    canvas.drawString(1 * cm, 0.5 * cm, usuario.apellido2)
    canvas.save()
    return filename


def generar_ficha(libro) -> str:
    """
    Genera una ficha de libro en formato PDF.

    Parámetros:
    -----------
    libro : Libro
        Instancia de la clase Libro para el cual se generará la ficha.

    Retorna:
    --------
    str
        Ruta del archivo PDF generado.
    """
    filename = os.path.join(tempfile.gettempdir(), f'ficha_{libro.isbn}.pdf')
    canvas = Canvas(filename, pagesize=(15 * cm, 10 * cm))
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(1 * cm, 9 * cm, 'Título: ')
    canvas.drawString(1 * cm, 8 * cm, 'Autor: ')
    canvas.drawString(1 * cm, 7 * cm, 'Editorial: ')
    canvas.drawString(1 * cm, 6 * cm, 'Año: ')
    canvas.drawString(1 * cm, 5 * cm, 'ISBN: ')
    canvas.setFont('Helvetica', 10)
    canvas.drawString(3 * cm, 9 * cm, libro.titulo)
    canvas.drawString(3 * cm, 8 * cm, libro.autor)
    canvas.drawString(3 * cm, 7 * cm, libro.editorial)
    canvas.drawString(3 * cm, 6 * cm, libro.anyo)
    canvas.drawString(3 * cm, 5 * cm, libro.isbn)

    caratula = GestorLibros.buscar_caratula(libro.isbn)
    if caratula:
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(1 * cm, 4 * cm, 'Carátula: ')
        canvas.drawImage(caratula, 3 * cm, 0.5 * cm, width=3 * cm, height=4 * cm)
    canvas.save()
    return filename


def generar_prestamos() -> str:
    """
    Genera un listado de préstamos en formato PDF.

    Retorna:
    --------
    str
        Ruta del archivo PDF generado.
    """
    elements = []
    filename = os.path.join(tempfile.gettempdir(), f'prestamos_{datetime.now().strftime("%y%m%d_%H%M%S")}.pdf')
    doc = SimpleDocTemplate(filename, pagesize=landscape(A4))

    gp = GestorPrestamos()
    gl = GestorLibros()
    gu = GestorUsuarios()
    data = [('ISBN', 'Título', 'Usuario', 'Nombre', 'Fecha')]

    for p in gp:
        l = gl.buscar_libro(p[0])
        u = gu.buscar_usuario(p[1]['usuario'])
        data.append((p[0],
                     l.titulo if len(l.titulo) < 25 else l.titulo[:25] + '...',
                     p[1]['usuario'],
                     str(u) if len(str(u)) < 25 else str(u)[:25] + '...',
                     p[1]['fecha'].strftime('%d/%m/%Y')))
    table = Table(data, colWidths=150, rowHeights=20)
    elements.append(table)
    doc.build(elements)
    return filename