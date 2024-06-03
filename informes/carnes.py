from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas


def generar_carne(usuario):
    filename = f'carne_{usuario.identificador}.pdf'
    canvas = Canvas(filename, pagesize=(8 * cm, 5 * cm))
    canvas.setFont('Helvetica', 12)
    canvas.drawCentredString(4 * cm, 4.5 * cm, 'Carné de Usuario')
    canvas.setFont('Helvetica-Bold', 8, )
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
