import io
import platform
from datetime import datetime
from flask import current_app

# Detectar el sistema operativo
SYSTEM = platform.system().lower()

# Inicializar variables
WEASYPRINT_AVAILABLE = False
HTML = None
CSS = None
FontConfiguration = None

# Solo intentar importar WeasyPrint si no estamos en Windows
if SYSTEM != 'windows':
    try:
        import weasyprint
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        WEASYPRINT_AVAILABLE = True
    except ImportError:
        WEASYPRINT_AVAILABLE = False
    except Exception:
        # Cualquier otro error (como problemas de dependencias)
        WEASYPRINT_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

def generar_vista_previa_html(profesor, asignacion, notas):
    """
    Genera el HTML para la vista previa del acta de evaluación
    """
    materia = asignacion.materia
    corte = asignacion.corte
    
    # Obtener estudiantes con notas para esta materia
    estudiantes_con_notas = []
    for nota in notas:
        estudiante = nota.estudiante
        estudiantes_con_notas.append({
            'cedula': estudiante.cedula,
            'nombre': estudiante.nombre,
            'apellido': estudiante.apellido,
            'nota': nota.nota
        })
    
    # Ordenar por apellido y nombre
    estudiantes_con_notas.sort(key=lambda x: (x['apellido'], x['nombre']))
    
    # Generar HTML del acta
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Acta de Evaluación</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                font-size: 12px;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #333;
                padding-bottom: 20px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                color: #333;
                font-weight: bold;
            }}
            .header h2 {{
                margin: 10px 0 0 0;
                font-size: 18px;
                color: #666;
                font-weight: bold;
            }}
            .info-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .info-table th, .info-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .info-table th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            .estudiantes-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .estudiantes-table th, .estudiantes-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            .estudiantes-table th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            .estudiantes-table td:nth-child(2), .estudiantes-table td:nth-child(3) {{
                text-align: left;
            }}
            .firmas-section {{
                margin-top: 40px;
                text-align: center;
            }}
            .firmas-section h3 {{
                margin: 20px 0 10px 0;
                font-size: 14px;
                font-weight: bold;
            }}
            .copias-info {{
                margin-top: 20px;
                text-align: center;
                font-size: 10px;
                font-weight: bold;
                color: #666;
            }}
            .no-estudiantes {{
                text-align: center;
                color: #666;
                font-style: italic;
                padding: 20px;
            }}
            @media print {{
                body {{
                    margin: 0;
                    padding: 10px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>ACTA DE EVALUACIÓN</h1>
                <h2>Materia: {materia.nombre}</h2>
            </div>
            
            <table class="info-table">
                <tr>
                    <th>Profesor:</th>
                    <td>{profesor.nombre} {profesor.apellido}</td>
                    <th>Corte:</th>
                    <td>{corte.seccion} - {corte.zona}</td>
                </tr>
                <tr>
                    <th>Código Materia:</th>
                    <td>{materia.codigo}</td>
                    <th>Fecha:</th>
                    <td>{datetime.now().strftime('%d/%m/%Y')}</td>
                </tr>
            </table>
            
            <table class="estudiantes-table">
                <thead>
                    <tr>
                        <th>N°</th>
                        <th>Apellidos</th>
                        <th>Nombres</th>
                        <th>Cédula</th>
                        <th>Nota</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    if estudiantes_con_notas:
        for i, estudiante in enumerate(estudiantes_con_notas, 1):
            html_content += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{estudiante['apellido']}</td>
                        <td>{estudiante['nombre']}</td>
                        <td>{estudiante['cedula']}</td>
                        <td>{estudiante['nota']}</td>
                    </tr>
            """
    else:
        html_content += """
                    <tr>
                        <td colspan="5" class="no-estudiantes">No hay estudiantes registrados con notas</td>
                    </tr>
        """
    
    html_content += f"""
                </tbody>
            </table>
            
            <div class="firmas-section">
                <h3>Firmas:</h3>
                <table class="firmas-table" style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 20px; text-align: center; width: 50%;">
                            <strong>Profesor</strong><br>
                            {profesor.nombre} {profesor.apellido}<br>
                            C.I.: {profesor.cedula}
                        </td>
                        <td style="border: 1px solid #ddd; padding: 20px; text-align: center; width: 50%;">
                            <strong>Coordinador</strong><br>
                            _________________<br>
                            C.I.: _________________
                        </td>
                    </tr>
                </table>
            </div>
            
            <div class="copias-info">
                <p>Original: Coordinación Académica</p>
                <p>Copia: Profesor</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

def generar_pdf_desde_html(html_content, nombre_archivo=None):
    """
    Convierte HTML a PDF usando WeasyPrint
    """
    if not WEASYPRINT_AVAILABLE:
        raise ImportError("WeasyPrint no está instalado. Instale con: pip install weasyprint")
    
    try:
        # Configurar fuentes
        font_config = FontConfiguration()
        
        # Crear el documento HTML
        html_doc = HTML(string=html_content)
        
        # Generar PDF
        pdf_bytes = html_doc.write_pdf(font_config=font_config)
        
        # Crear buffer de memoria
        pdf_buffer = io.BytesIO(pdf_bytes)
        pdf_buffer.seek(0)
        
        return pdf_buffer
        
    except Exception as e:
        raise Exception(f"Error al generar PDF: {str(e)}")

def generar_pdf_notas_materia(profesor, asignacion, notas, usar_html=True, incluir_vista_previa=False):
    """
    Genera un PDF con las notas de los estudiantes para una materia específica
    
    Args:
        profesor: Objeto Profesor
        asignacion: Objeto AsignacionMateria
        notas: Lista de objetos Nota
        usar_html: Si usar HTML para generar PDF (requiere WeasyPrint)
        incluir_vista_previa: Si incluir también la vista previa HTML
    
    Returns:
        Si incluir_vista_previa=True: (pdf_buffer, vista_previa_html)
        Si incluir_vista_previa=False: pdf_buffer
    """
    
    # Generar el HTML del acta
    html_content = generar_vista_previa_html(profesor, asignacion, notas)
    
    # En Windows, usar ReportLab por defecto
    if SYSTEM == 'windows':
        usar_html = False
    
    if incluir_vista_previa:
        # Retornar tanto el PDF como la vista previa HTML
        if usar_html and WEASYPRINT_AVAILABLE:
            try:
                pdf_buffer = generar_pdf_desde_html(html_content)
                return pdf_buffer, html_content
            except Exception:
                # Fallback: solo retornar HTML si no se puede generar PDF
                return None, html_content
        else:
            # Solo retornar HTML si no se usa HTML para PDF
            return None, html_content
    else:
        # Solo retornar el PDF
        if usar_html and WEASYPRINT_AVAILABLE:
            try:
                return generar_pdf_desde_html(html_content)
            except Exception:
                # Fallback a ReportLab si WeasyPrint no está disponible
                if REPORTLAB_AVAILABLE:
                    return generar_pdf_con_reportlab(profesor, asignacion, notas)
                else:
                    raise ImportError("ReportLab no está instalado. Instale con: pip install reportlab")
        else:
            # Usar ReportLab directamente
            if REPORTLAB_AVAILABLE:
                return generar_pdf_con_reportlab(profesor, asignacion, notas)
            else:
                raise ImportError("ReportLab no está instalado. Instale con: pip install reportlab")

def generar_pdf_con_reportlab(profesor, asignacion, notas):
    """
    Genera un PDF usando ReportLab como alternativa a WeasyPrint
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("ReportLab no está instalado. Instale con: pip install reportlab")
    
    materia = asignacion.materia
    corte = asignacion.corte
    
    # Obtener estudiantes con notas para esta materia
    estudiantes_con_notas = []
    for nota in notas:
        estudiante = nota.estudiante
        estudiantes_con_notas.append({
            'cedula': estudiante.cedula,
            'nombre': estudiante.nombre,
            'apellido': estudiante.apellido,
            'nota': nota.nota
        })
    
    # Ordenar por apellido y nombre
    estudiantes_con_notas.sort(key=lambda x: (x['apellido'], x['nombre']))
    
    # Crear buffer para el PDF
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=1  # Centrado
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
        alignment=1  # Centrado
    )
    
    # Contenido del PDF
    story = []
    
    # Título
    story.append(Paragraph("ACTA DE EVALUACIÓN", title_style))
    story.append(Paragraph(f"Materia: {materia.nombre}", subtitle_style))
    story.append(Spacer(1, 20))
    
    # Información del profesor y corte
    info_data = [
        ['Profesor:', f"{profesor.nombre} {profesor.apellido}", 'Corte:', f"{corte.seccion} - {corte.zona}"],
        ['Código Materia:', materia.codigo, 'Fecha:', datetime.now().strftime('%d/%m/%Y')]
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 3*inch, 1.5*inch, 2*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Tabla de estudiantes
    if estudiantes_con_notas:
        # Encabezados
        headers = ['N°', 'Apellidos', 'Nombres', 'Cédula', 'Nota']
        table_data = [headers]
        
        # Datos de estudiantes
        for i, estudiante in enumerate(estudiantes_con_notas, 1):
            table_data.append([
                str(i),
                estudiante['apellido'],
                estudiante['nombre'],
                estudiante['cedula'],
                str(estudiante['nota'])
            ])
        
        # Crear tabla
        estudiantes_table = Table(table_data, colWidths=[0.5*inch, 2*inch, 2*inch, 1.5*inch, 0.8*inch])
        estudiantes_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (2, -1), 'LEFT'),  # Apellidos y nombres alineados a la izquierda
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Encabezados en negrita
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ]))
        story.append(estudiantes_table)
    else:
        story.append(Paragraph("No hay estudiantes registrados con notas", styles['Normal']))
    
    story.append(Spacer(1, 30))
    
    # Sección de firmas
    story.append(Paragraph("Firmas:", styles['Heading3']))
    story.append(Spacer(1, 10))
    
    firmas_data = [
        ['Profesor', 'Coordinador'],
        [f"{profesor.nombre} {profesor.apellido}", "_________________"],
        [f"C.I.: {profesor.cedula}", "C.I.: _________________"]
    ]
    
    firmas_table = Table(firmas_data, colWidths=[4*inch, 4*inch])
    firmas_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(firmas_table)
    
    story.append(Spacer(1, 20))
    
    # Información de copias
    copias_style = ParagraphStyle(
        'Copias',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1  # Centrado
    )
    story.append(Paragraph("Original: Coordinación Académica", copias_style))
    story.append(Paragraph("Copia: Profesor", copias_style))
    
    # Generar PDF
    doc.build(story)
    pdf_buffer.seek(0)
    
    return pdf_buffer

def generar_pdf_acta_completa(profesor, asignacion, notas):
    """
    Genera un PDF completo del acta de evaluación
    """
    return generar_pdf_notas_materia(profesor, asignacion, notas, usar_html=True)
