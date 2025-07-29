# Flask imports
from flask import (
    render_template, redirect, url_for, flash, request, 
    send_file, jsonify, Response, render_template_string
)
import io
import os
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from modulos.profesores import bp
from modulos import db
from modulos.profesores.models import Profesor
from modulos.control_academico.models import (
    Materia, Corte, Inscripcion, Nota, Programa, AsignacionMateria
)
from modulos.estudiantes.models import Estudiante
from modulos.central.models import Persona

@bp.route('/')
def index():
    profesores = Profesor.query.all()
    return render_template('profesores/listar_profesores.html', profesores=profesores)

@bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_profesor():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        cedula = request.form['cedula']
        if not cedula.isdigit() or len(cedula) < 8:
            flash('La cédula debe contener al menos 8 dígitos y solo números.', 'error')
            return render_template('profesores/form_profesor.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=request.form['telefono'], correo=request.form['correo'], usuario=request.form['usuario'], titulo=request.form['titulo'])
        numero_telefono = request.form['telefono']
        correo_electronico = request.form['correo']
        usuario = request.form['usuario']
        contrasenia = cedula
        rol = 'profesor'
        titulo = request.form['titulo']
        # Validaciones de unicidad reforzadas usando Persona
        if Persona.query.filter_by(cedula=cedula).first():
            flash('Ya existe un usuario con esa cédula en el sistema.', 'error')
            return render_template('profesores/form_profesor.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=numero_telefono, correo=correo_electronico, usuario=usuario, titulo=titulo)
        if Persona.query.filter_by(usuario=usuario).first():
            flash('Ya existe un usuario con ese nombre en el sistema.', 'error')
            return render_template('profesores/form_profesor.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=numero_telefono, correo=correo_electronico, usuario=usuario, titulo=titulo)
        if Persona.query.filter_by(correo_electronico=correo_electronico).first():
            flash('Ya existe un usuario con ese correo electrónico en el sistema.', 'error')
            return render_template('profesores/form_profesor.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=numero_telefono, correo=correo_electronico, usuario=usuario, titulo=titulo)
        profesor = Profesor(
            cedula=cedula,
            nombre=nombre,
            apellido=apellido,
            numero_telefono=numero_telefono,
            correo_electronico=correo_electronico,
            usuario=usuario,
            contrasenia=contrasenia,
            rol=rol,
            titulo=titulo
        )
        try:
            db.session.add(profesor)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Error: El usuario, correo o cédula ya existen.', 'error')
            return render_template('profesores/form_profesor.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=numero_telefono, correo=correo_electronico, usuario=usuario, titulo=titulo)
        flash('Profesor registrado exitosamente', 'success')
        return redirect(url_for('profesores.index'))
    return render_template('profesores/form_profesor.html')

@bp.route('/editar/<cedula>', methods=['GET', 'POST'])
def editar_profesor(cedula):
    profesor = Profesor.query.get_or_404(cedula)
    if request.method == 'POST':
        nueva_cedula = request.form['cedula']
        nuevo_usuario = request.form['usuario']
        nuevo_correo = request.form['correo']

        # Verificar unicidad de cédula (si cambió)
        if nueva_cedula != profesor.cedula and Profesor.query.filter_by(cedula=nueva_cedula).first():
            flash('Ya existe un profesor con esa cédula.', 'error')
            return render_template('profesores/form_profesor.html', profesor=profesor)

        # Verificar unicidad de usuario
        usuario_existente = Profesor.query.filter(
            Profesor.usuario == nuevo_usuario,
            Profesor.cedula != profesor.cedula
        ).first()
        if usuario_existente:
            flash('Ya existe un profesor con ese nombre de usuario.', 'error')
            return render_template('profesores/form_profesor.html', profesor=profesor)

        # Verificar unicidad de correo
        correo_existente = Profesor.query.filter(
            Profesor.correo_electronico == nuevo_correo,
            Profesor.cedula != profesor.cedula
        ).first()
        if correo_existente:
            flash('Ya existe un profesor con ese correo electrónico.', 'error')
            return render_template('profesores/form_profesor.html', profesor=profesor)

        # Si la cédula cambió, crear nuevo registro y borrar el anterior
        if nueva_cedula != profesor.cedula:
            db.session.delete(profesor)
            db.session.commit()
            nuevo_profesor = Profesor(
                cedula=nueva_cedula,
                nombre=request.form['nombre'],
                apellido=request.form['apellido'],
                numero_telefono=request.form['telefono'],
                correo_electronico=nuevo_correo,
                usuario=nuevo_usuario,
                contrasenia=nueva_cedula,
                rol='profesor',
                titulo=request.form['titulo']
            )
            db.session.add(nuevo_profesor)
            db.session.commit()
            flash('Profesor actualizado exitosamente (cédula cambiada)', 'success')
            return redirect(url_for('profesores.index'))

        # Si la cédula no cambió, actualizar campos
        profesor.nombre = request.form['nombre']
        profesor.apellido = request.form['apellido']
        profesor.numero_telefono = request.form['telefono']
        profesor.correo_electronico = nuevo_correo
        profesor.usuario = nuevo_usuario
        profesor.contrasenia = profesor.cedula
        profesor.titulo = request.form['titulo']
        db.session.commit()
        flash('Profesor actualizado exitosamente', 'success')
        return redirect(url_for('profesores.index'))

    return render_template('profesores/form_profesor.html', profesor=profesor)

@bp.route('/eliminar/<cedula>')
def eliminar_profesor(cedula):
    profesor = Profesor.query.get_or_404(cedula)
    try:
        db.session.delete(profesor)
        db.session.commit()
        flash('Profesor eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar profesor: {str(e)}', 'danger')
    return redirect(url_for('profesores.index'))

@bp.route('/profesores/<cedula>/materias')
def materias_profesor(cedula):
    profesor = Profesor.query.get_or_404(cedula)
    
    # Obtener asignaciones del profesor
    asignaciones = AsignacionMateria.query.filter_by(profesor_id=cedula).all()
    
    # Obtener todas las materias disponibles
    materias = Materia.query.all()
    
    # Obtener todos los cortes disponibles
    cortes = Corte.query.all()
    
    return render_template('profesores/materias.html', 
                         profesor=profesor, 
                         asignaciones=asignaciones,
                         materias=materias,
                         cortes=cortes)

@bp.route('/profesores/<cedula>/materias/asignar', methods=['GET', 'POST'])
def asignar_materia(cedula):
    profesor = Profesor.query.get_or_404(cedula)
    
    if request.method == 'POST':
        materia_codigo = request.form.get('materia_codigo')
        corte_id = request.form.get('corte_id')
        
        if not materia_codigo or not corte_id:
            flash('Debe seleccionar una materia y un corte', 'error')
            return redirect(url_for('profesores.materias_profesor', cedula=cedula))
        
        # Verificar si ya existe una asignación para esta materia-corte
        asignacion_existente = AsignacionMateria.query.filter_by(
            materia_codigo=materia_codigo,
            corte_id=corte_id
        ).first()
        
        if asignacion_existente:
            flash('Esta materia ya está asignada a otro profesor en este corte', 'error')
            return redirect(url_for('profesores.materias_profesor', cedula=cedula))
        
        # Verificar si el profesor ya tiene esta materia asignada
        asignacion_profesor = AsignacionMateria.query.filter_by(
            profesor_id=cedula,
            materia_codigo=materia_codigo,
            corte_id=corte_id
        ).first()
        
        if asignacion_profesor:
            flash('Ya tienes asignada esta materia en este corte', 'error')
            return redirect(url_for('profesores.materias_profesor', cedula=cedula))
        
        try:
            nueva_asignacion = AsignacionMateria(
                profesor_id=cedula,
                materia_codigo=materia_codigo,
                corte_id=corte_id
            )
            db.session.add(nueva_asignacion)
            db.session.commit()
            flash('Materia asignada exitosamente', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Error: Ya existe una asignación para esta combinación de materia y corte', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al asignar la materia: {str(e)}', 'error')
        
        return redirect(url_for('profesores.materias_profesor', cedula=cedula))
    
    # Obtener los códigos de materias ya asignadas al profesor en cualquier corte
    asignaciones = AsignacionMateria.query.filter_by(profesor_id=cedula).all()
    materias_asignadas = {a.materia_codigo for a in asignaciones}
    
    # Filtrar materias que NO están asignadas al profesor
    materias = Materia.query.filter(~Materia.codigo.in_(materias_asignadas)).all()
    cortes = Corte.query.all()
    return render_template('profesores/asignar_materia.html', 
                         profesor=profesor, 
                         materias=materias, 
                         cortes=cortes)

@bp.route('/profesores/<cedula>/materias/<int:asignacion_id>/desasignar')
def desasignar_materia(cedula, asignacion_id):
    profesor = Profesor.query.get_or_404(cedula)
    asignacion = AsignacionMateria.query.get_or_404(asignacion_id)
    
    # Verificar que la asignación pertenece al profesor
    if asignacion.profesor_id != cedula:
        flash('No tiene permiso para desasignar esta materia', 'error')
        return redirect(url_for('profesores.materias_profesor', cedula=cedula))
    
    try:
        db.session.delete(asignacion)
        db.session.commit()
        flash('Materia desasignada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al desasignar la materia: {str(e)}', 'error')
    
    return redirect(url_for('profesores.materias_profesor', cedula=cedula))

@bp.route('/materias/<cedula>/eliminar/<codigo>')
def eliminar_materia(cedula, codigo):
    profesor = Profesor.query.get_or_404(cedula)
    materia = Materia.query.get_or_404(codigo)
    
    # Verificar que la materia pertenece al profesor
    asignacion = AsignacionMateria.query.filter_by(
        profesor_id=cedula,
        materia_codigo=codigo
    ).first()
    
    if not asignacion:
        flash('No tiene permiso para eliminar esta materia', 'error')
        return redirect(url_for('profesores.materias_profesor', cedula=cedula))
    
    try:
        # Eliminar la asignación
        db.session.delete(asignacion)
        db.session.commit()
        flash('Materia eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la materia: {str(e)}', 'error')
    
    return redirect(url_for('profesores.materias_profesor', cedula=cedula))

@bp.route('/profesores/<cedula>/notas')
def notas_profesor(cedula):
    profesor = Profesor.query.get_or_404(cedula)
    
    # Obtener las asignaciones del profesor
    asignaciones = AsignacionMateria.query.filter_by(profesor_id=cedula).all()
    
    # Obtener todas las notas de las materias asignadas al profesor
    notas = []
    for asignacion in asignaciones:
        notas_materia = Nota.query.filter_by(materia_codigo=asignacion.materia_codigo).all()
        notas.extend(notas_materia)
    
    return render_template('profesores/notas.html', 
                         profesor=profesor, 
                         notas=notas,
                         asignaciones=asignaciones)

@bp.route('/profesores/<cedula>/notas/<estudiante_cedula>/<materia_codigo>', methods=['GET', 'POST'])
def editar_nota(cedula, estudiante_cedula, materia_codigo):
    profesor = Profesor.query.get_or_404(cedula)
    estudiante = Estudiante.query.get_or_404(estudiante_cedula)
    materia = Materia.query.get_or_404(materia_codigo)
    
    # Verificar que el profesor tiene asignada esta materia
    asignacion = AsignacionMateria.query.filter_by(
        profesor_id=cedula,
        materia_codigo=materia_codigo
    ).first()
    
    if not asignacion:
        flash('No tiene permiso para editar notas de esta materia', 'error')
        return redirect(url_for('profesores.notas_profesor', cedula=cedula))
    
    # Buscar la nota existente o crear una nueva
    nota = Nota.query.filter_by(
        estudiante_id=estudiante_cedula,
        materia_codigo=materia_codigo
    ).first()
    
    if request.method == 'POST':
        nueva_nota = float(request.form['nota'])
        
        if nueva_nota < 0 or nueva_nota > 10:
            flash('La nota debe estar entre 0 y 10', 'error')
            return render_template('profesores/editar_nota.html', 
                                profesor=profesor, 
                                estudiante=estudiante, 
                                materia=materia, 
                                nota=nota)

@bp.route('/profesores/<cedula>/crear_acta_pdf/<materia_codigo>')
def crear_acta_pdf(cedula, materia_codigo):
    profesor = Profesor.query.get_or_404(cedula)
    materia = Materia.query.get_or_404(materia_codigo)

    asignacion = AsignacionMateria.query.filter_by(
        profesor_id=cedula,
        materia_codigo=materia_codigo
    ).first()

    if not asignacion:
        flash('No tiene permiso para generar acta de esta materia', 'error')
        return redirect(url_for('profesores.notas_profesor', cedula=cedula))

    estudiantes_inscritos = Inscripcion.query.filter_by(corte_id=asignacion.corte_id).all()

    if not estudiantes_inscritos:
        flash('No hay estudiantes inscritos en este corte para generar el acta', 'warning')
        return redirect(url_for('profesores.notas_profesor', cedula=cedula))

    notas = []
    for inscripcion in estudiantes_inscritos:
        nota = Nota.query.filter_by(estudiante_id=inscripcion.estudiante_id, materia_codigo=materia_codigo).first()
        if nota:
            notas.append(nota)

    buffer = io.BytesIO()
    # Configurar márgenes: (izquierda, arriba, derecha, abajo) en pulgadas
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        leftMargin=0.5*inch,    # Margen izquierdo
        rightMargin=0.5*inch,   # Margen derecho (igual al izquierdo)
        topMargin=0.3*inch,     # Margen superior reducido
        bottomMargin=0.5*inch   # Margen inferior
    )
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=14, alignment=1, fontName='Helvetica-Bold')
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Heading2'], fontSize=12, alignment=1, fontName='Helvetica-Bold')
    custom_normal = ParagraphStyle('CustomNormal', fontName='Helvetica', fontSize=9, leading=10)

    # Logo y título
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'logo_udo.jpg')
    logo = Image(logo_path, width=1*inch, height=1*inch)
    header_data = [[logo, Paragraph("<b>UNIVERSIDAD DE ORIENTE</b><br/>POSTGRADO - ACTA DE EVALUACIÓN", title_style)]]
    header_table = Table(header_data, colWidths=[1.2*inch, 5.8*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), 
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black)  # Bordes para toda la tabla
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 12))

    # Info del curso
    def obtener_nombre_mes(numero_mes):
        meses = {
            1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL',
            5: 'MAYO', 6: 'JUNIO', 7: 'JULIO', 8: 'AGOSTO',
            9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'
        }
        return meses.get(numero_mes, '')
    
    mes_fin = obtener_nombre_mes(asignacion.corte.fecha_fin.month)
    lapso_texto = f"{mes_fin} - {asignacion.corte.fecha_fin.strftime('%Y')}"
    
    info_data = [
        ["CÓDIGO:", "ASIGNATURA:",  "SECC:",'AÑO', "PER:","LAPSO:"],
        [materia.codigo, materia.nombre.upper(), asignacion.corte.seccion.upper(), asignacion.corte.fecha_fin.strftime('%Y'), ' ' , lapso_texto]
    ]
    info_table = Table(info_data, colWidths=[0.8*inch, 1.2*inch, 1.2*inch, 1.5*inch, 0.8*inch, 1.3*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('GRID', (0,0), (-1,-1), 1, colors.black)  # Bordes para toda la tabla
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 10))

    # Profesor
    elements.append(Paragraph("PROFESOR", subtitle_style))
    
    # Crear estilos centrados para el profesor
    profesor_nombre_style = ParagraphStyle('ProfesorNombre', parent=custom_normal, alignment=1)  # 1 = centrado
    profesor_cedula_style = ParagraphStyle('ProfesorCedula', parent=custom_normal, alignment=1)  # 1 = centrado
    
    elements.append(Paragraph(f"{profesor.nombre.upper()} {profesor.apellido.upper()}", profesor_nombre_style))
    elements.append(Paragraph(f"V-{profesor.cedula}", profesor_cedula_style))
    elements.append(Spacer(1, 10))

    # Tabla encabezados
    headers = ['N°', 'CEDULA DE IDENTIDAD', 'APELLIDOS Y NOMBRES', 'TIPO EXAMEN', 'CALIFICACIÓN', '']
    calificacion_row = ['', '', '', '', 'N°', 'LETRAS']
    table_data = [headers, calificacion_row]

    def numero_a_letras(numero):
        return ["CERO", "UNO", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE", "DIEZ"][numero] if isinstance(numero, int) and 0 <= numero <= 10 else "NC"

    for i, inscripcion in enumerate(estudiantes_inscritos, 1):
        estudiante = inscripcion.estudiante
        nota_estudiante = next((nota for nota in notas if nota.estudiante_id == estudiante.cedula), None)
        if nota_estudiante:
            numero_nota = int(nota_estudiante.nota) if nota_estudiante.nota.is_integer() else ""
            letras_nota = numero_a_letras(numero_nota) if numero_nota != "" else "NC"
        else:
            numero_nota = ""
            letras_nota = "NC"

        row = [
            f"{i:02d}",
            f"V-{estudiante.cedula}",
            f"{estudiante.apellido.upper()} {estudiante.nombre.upper()}",
            "F",
            str(numero_nota),
            letras_nota
        ]
        table_data.append(row)

    while len(table_data) < 19:
        table_data.append([f"{len(table_data)-1:02d}", "", "", "", "", ""])

    col_widths = [0.5*inch, 1.5*inch, 2.5*inch, 1.0*inch, 0.5*inch, 1*inch]
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,1), colors.grey),
        ('ALIGN', (2,2), (2,-1), 'LEFT'),
        ('ALIGN', (4,2), (4,-1), 'RIGHT'),
        ('ALIGN', (3,2), (3,-1), 'CENTER'),
        ('SPAN', (4,0), (5,0))
    ]))
    elements.append(table)
    elements.append(Spacer(1, 15))

    #valido sin enmiendas
    valido_style = ParagraphStyle('Validado', parent=custom_normal, fontSize=7, alignment=1, fontName='Helvetica-Bold')  # Fuente más pequeña y centrada
    elements.append(Paragraph("VALIDO SIN ENMIENDAS", valido_style))
    elements.append(Spacer(1, 10))

    # Firmas
    firmas_data = [
        ["", "RECIBIDO Y REFRENDADO POR", "RECIBIDO Y REFRENDADO POR"],
        ["_" * 20, "_" * 20, "_" * 20],
        [f"{profesor.nombre.upper()} {profesor.apellido.upper()}", "VICTOR MUJICA (E)", "STEFANO BONOLI"],
        [f"V-{profesor.cedula}", "", ""],
        ["PROFESOR", "COORDINADOR DEL PROGRAMA", "D.A.C.E"]
    ]
    firmas_table = Table(firmas_data, colWidths=[2*inch, 2*inch, 2*inch])
    firmas_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('FONTNAME', (0,0), (-1,1), 'Helvetica-Bold'),  # Primera y segunda fila en negrita
        ('FONTSIZE', (0,0), (-1,1), 9),  # Tamaño de fuente para los títulos
        ('SPAN', (0,0), (0,0)),  # Evitar que se divida el texto
        ('SPAN', (1,0), (1,0)),
        ('SPAN', (2,0), (2,0)),
        ('SPAN', (0,1), (0,1)),  # Para la segunda fila
        ('SPAN', (1,1), (1,1)),
        ('SPAN', (2,1), (2,1)),
        ('GRID', (0,0), (-1,-1), 1, colors.black),  # Bordes para toda la tabla
        ('TOPPADDING', (0,1), (-1,1), 20),  # Más espacio sobre las líneas de firma (fila 1)
        ('BOTTOMPADDING', (0,1), (-1,1), 5)  # Espacio inferior de las líneas de firma
    ]))
    elements.append(firmas_table)
    elements.append(Spacer(1, 20))

    # Copias
    copias_style = ParagraphStyle('Copias', parent=custom_normal, fontSize=7, alignment=1)  # Fuente más pequeña y centrada
    elements.append(Paragraph(
        "ORIGINAL:D.A.C.E    1ra COPIA: COMPUTACIÓN    2da COPIA: Coord. DEL PROGRAMA    3ra COPIA: CONCEJO DE ESTUDIOS DE POSTGRADO",
        copias_style))

    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'acta_evaluacion_{materia.nombre}_{profesor.apellido}.pdf',
        mimetype='application/pdf'
    )

