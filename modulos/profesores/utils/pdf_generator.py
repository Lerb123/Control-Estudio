from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime

def generar_pdf_notas_materia(profesor, asignacion, notas):
    """
    Genera un PDF con las notas de los estudiantes para una materia específica
    
    Args:
        profesor: Objeto Profesor
        asignacion: Objeto AsignacionMateria específico
        notas: Lista de notas de los estudiantes para esa materia
    
    Returns:
        BytesIO: Contenido del PDF en bytes
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
        alignment=TA_LEFT
    )
    
    # Título del documento
    titulo = f"REPORTE DE NOTAS - {asignacion.materia.nombre}"
    story.append(Paragraph(titulo, title_style))
    story.append(Spacer(1, 20))
    
    # Información del profesor
    info_profesor = f"<b>Profesor:</b> {profesor.nombre} {profesor.apellido}<br/>"
    info_profesor += f"<b>Cédula:</b> {profesor.cedula}<br/>"
    info_profesor += f"<b>Título:</b> {profesor.titulo}<br/>"
    info_profesor += f"<b>Fecha de Generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    
    story.append(Paragraph(info_profesor, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Información de la materia
    materia_info = f"<b>Materia:</b> {asignacion.materia.nombre}<br/>"
    materia_info += f"<b>Código:</b> {asignacion.materia.codigo}<br/>"
    materia_info += f"<b>Programa:</b> {asignacion.materia.programa.nombre}<br/>"
    materia_info += f"<b>Corte:</b> {asignacion.corte.seccion} - {asignacion.corte.zona}"
    
    story.append(Paragraph(materia_info, styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Obtener estudiantes inscritos en este corte
    estudiantes_inscritos = asignacion.corte.inscripciones
    
    if estudiantes_inscritos:
        # Crear tabla de notas
        data = [['#', 'Estudiante', 'Cédula', 'Estado Pago', 'Nota']]
        
        for i, inscripcion in enumerate(estudiantes_inscritos, 1):
            estudiante = inscripcion.estudiante
            
            # Buscar nota del estudiante para esta materia
            nota_estudiante = next(
                (n for n in notas if n.estudiante_id == estudiante.cedula and n.materia_codigo == asignacion.materia.codigo),
                None
            )
            
            # Estado de pago
            estado_pago = "Pagado" if inscripcion.estado_pago else "Pendiente"
            
            # Nota
            nota_texto = f"{nota_estudiante.nota}/20" if nota_estudiante else "No asignada"
            
            data.append([
                str(i),
                f"{estudiante.nombre} {estudiante.apellido}",
                estudiante.cedula,
                estado_pago,
                nota_texto
            ])
        
        # Crear tabla
        table = Table(data, colWidths=[0.5*inch, 2.2*inch, 1.2*inch, 1*inch, 1*inch])
        
        # Estilo de la tabla
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        table.setStyle(table_style)
        story.append(table)
        
        # Estadísticas
        story.append(Spacer(1, 20))
        total_estudiantes = len(estudiantes_inscritos)
        estudiantes_con_nota = len([n for n in notas if n.materia_codigo == asignacion.materia.codigo])
        estudiantes_pagados = len([i for i in estudiantes_inscritos if i.estado_pago])
        
        estadisticas = f"<b>Estadísticas:</b><br/>"
        estadisticas += f"• Total de estudiantes: {total_estudiantes}<br/>"
        estadisticas += f"• Estudiantes con nota asignada: {estudiantes_con_nota}<br/>"
        estadisticas += f"• Estudiantes con pago completo: {estudiantes_pagados}"
        
        story.append(Paragraph(estadisticas, styles['Normal']))
        
    else:
        # No hay estudiantes inscritos
        story.append(Paragraph("No hay estudiantes inscritos en este corte.", styles['Normal']))
    
    # Construir el PDF
    doc.build(story)
    buffer.seek(0)
    return buffer 