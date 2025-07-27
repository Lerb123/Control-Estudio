from flask import render_template, redirect, url_for, flash, request, send_file, jsonify, Response
from modulos.profesores import bp
from modulos import db
from modulos.profesores.models import Profesor
from modulos.control_academico.models import Materia, Corte, Inscripcion, Nota, Programa, AsignacionMateria
from modulos.estudiantes.models import Estudiante
from sqlalchemy.exc import IntegrityError
from modulos.central.models import Persona
from datetime import datetime
from flask import render_template_string
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import os

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
    
    # Verificar que el profesor tiene asignada esta materia
    asignacion = AsignacionMateria.query.filter_by(
        profesor_id=cedula,
        materia_codigo=materia_codigo
    ).first()
    
    if not asignacion:
        flash('No tiene permiso para generar acta de esta materia', 'error')
        return redirect(url_for('profesores.notas_profesor', cedula=cedula))
    
    # Obtener todas las notas de la materia
    notas = Nota.query.filter_by(materia_codigo=materia_codigo).all()
    
    # Crear el PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1,  # Centrado
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=15,
        alignment=1,  # Centrado
        fontName='Helvetica-Bold'
    )
    
    # Encabezado
    elements.append(Paragraph("UNIVERSIDAD DE ORIENTE", title_style))
    elements.append(Paragraph("POSTGRADO - ACTA DE EVALUACIÓN", subtitle_style))
    elements.append(Spacer(1, 20))
    
    # Información del curso
    curso_data = [
        ['CODIGO', 'ASIGNATURA', 'SECC', 'AÑO', 'PER', 'LAPSO'],
        [str(materia.codigo), materia.nombre.upper(), 'GGIA', '2024', '', 'diciembre - 2024']
    ]
    
    curso_table = Table(curso_data, colWidths=[1*inch, 2.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.5*inch])
    curso_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ]))
    elements.append(curso_table)
    elements.append(Spacer(1, 15))
    
    # Información del profesor
    elements.append(Paragraph("PROFESOR", subtitle_style))
    elements.append(Paragraph(f"{profesor.apellido} {profesor.nombre}", styles['Normal']))
    elements.append(Paragraph(f"V-{profesor.cedula}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Tabla de estudiantes y notas
    headers = ['N°', 'CEDULA DE IDENTIDAD', 'APELLIDOS Y NOMBRES', 'TIPO EXAMEN', 'CALIFICACION']
    calificacion_headers = ['N°', 'LETRAS']
    
    # Crear tabla con subcolumnas para calificación
    table_data = [headers]
    
    # Agregar subheaders para calificación
    calificacion_row = ['', '', '', '', 'N°', 'LETRAS']
    table_data.append(calificacion_row)
    
    # Función para convertir número a letras
    def numero_a_letras(numero):
        if numero == 0:
            return "CERO"
        elif numero == 1:
            return "UNO"
        elif numero == 2:
            return "DOS"
        elif numero == 3:
            return "TRES"
        elif numero == 4:
            return "CUATRO"
        elif numero == 5:
            return "CINCO"
        elif numero == 6:
            return "SEIS"
        elif numero == 7:
            return "SIETE"
        elif numero == 8:
            return "OCHO"
        elif numero == 9:
            return "NUEVE"
        elif numero == 10:
            return "DIEZ"
        else:
            return "NC"
    
    # Agregar datos de estudiantes
    for i, nota in enumerate(notas, 1):
        estudiante = nota.estudiante
        numero_nota = int(nota.nota) if nota.nota.is_integer() else nota.nota
        letras_nota = numero_a_letras(int(nota.nota)) if nota.nota.is_integer() else "NC"
        
        row = [
            f"{i:02d}",
            f"V-{estudiante.cedula}",
            f"{estudiante.apellido} {estudiante.nombre}",
            "F",  # Tipo examen (Final)
            str(numero_nota),
            letras_nota
        ]
        table_data.append(row)
    
    # Si no hay suficientes estudiantes, agregar filas vacías hasta 25
    while len(table_data) < 27:  # 2 headers + 25 estudiantes
        row = [f"{len(table_data)-1:02d}", "", "", "", "", ""]
        table_data.append(row)
    
    # Crear tabla
    col_widths = [0.5*inch, 1.5*inch, 2.5*inch, 0.8*inch, 0.5*inch, 1*inch]
    table = Table(table_data, colWidths=col_widths)
    
    # Estilos de la tabla
    table_style = [
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 1), colors.grey),
        ('ALIGN', (1, 2), (2, -1), 'LEFT'),  # Cédula y nombres alineados a la izquierda
        ('ALIGN', (4, 2), (5, -1), 'LEFT'),  # Letras alineadas a la izquierda
        ('ALIGN', (3, 2), (3, -1), 'CENTER'),  # Tipo examen centrado
        ('ALIGN', (4, 2), (4, -1), 'RIGHT'),  # Números de calificación a la derecha
        ('SPAN', (4, 0), (5, 0)),  # Combinar celdas para "CALIFICACION"
    ]
    
    table.setStyle(TableStyle(table_style))
    elements.append(table)
    elements.append(Spacer(1, 30))
    
    # Línea de validación
    elements.append(Paragraph("_" * 80, styles['Normal']))
    elements.append(Paragraph("VALIDO SIN ENMIENDAS", styles['Normal']))
    elements.append(Paragraph("_" * 80, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Firmas
    elements.append(Paragraph("RECIBIDO Y REFRENDADO POR", subtitle_style))
    elements.append(Spacer(1, 30))
    
    # Tabla de firmas
    firmas_data = [
        ["ABRAHAN ANDREWS", "VICTOR MUJICA (E)", "STEFANO BONOLI"],
        ["V-8.297.067", "COORDINADOR DEL PROGRAMA", "D.A.C.E"],
        ["PROFESOR", "", ""]
    ]
    
    firmas_table = Table(firmas_data, colWidths=[2*inch, 2*inch, 2*inch])
    firmas_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 0), (0, 0), 1, colors.black),
        ('LINEBELOW', (1, 0), (1, 0), 1, colors.black),
        ('LINEBELOW', (2, 0), (2, 0), 1, colors.black),
    ]))
    elements.append(firmas_table)
    elements.append(Spacer(1, 20))
    
    # Información de copias
    copias_text = "ORIGINAL:D.A.C.E    1ra COPIA: COMPUTACION    2da COPIA: Coord. DEL PROGRAMA    3ra COPIA: CONCEJO DE ESTUDIOS DE POSTGRADO"
    elements.append(Paragraph(copias_text, styles['Normal']))
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'acta_evaluacion_{materia.nombre}_{profesor.apellido}.pdf',
        mimetype='application/pdf'
    )
