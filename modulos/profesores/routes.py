from flask import render_template, redirect, url_for, flash, request
from modulos.profesores import bp
from modulos import db
from modulos.profesores.models import Profesor
from modulos.control_academico.models import Materia, Corte, Inscripcion, Nota, Programa, AsignacionMateria
from modulos.estudiantes.models import Estudiante
from sqlalchemy.exc import IntegrityError
from modulos.central.models import Persona
from datetime import datetime

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
        
        if nueva_nota < 0 or nueva_nota > 20:
            flash('La nota debe estar entre 0 y 20', 'error')
            return render_template('profesores/editar_nota.html', 
                                profesor=profesor, 
                                estudiante=estudiante, 
                                materia=materia, 
                                nota=nota)
        
        try:
            if nota:
                nota.nota = nueva_nota
                nota.fecha_registro = datetime.utcnow()
            else:
                nueva_nota_obj = Nota(
                    estudiante_id=estudiante_cedula,
                    materia_codigo=materia_codigo,
                    nota=nueva_nota
                )
                db.session.add(nueva_nota_obj)
            
            db.session.commit()
            flash('Nota actualizada exitosamente', 'success')
            return redirect(url_for('profesores.notas_profesor', cedula=cedula))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la nota: {str(e)}', 'error')
    
    return render_template('profesores/editar_nota.html', 
                         profesor=profesor, 
                         estudiante=estudiante, 
                         materia=materia, 
                         nota=nota)
