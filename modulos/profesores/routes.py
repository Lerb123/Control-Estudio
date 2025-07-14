from flask import render_template, redirect, url_for, flash, request
from modulos.profesores import bp
from modulos import db
from modulos.profesores.models import Profesor
from modulos.control_academico.models import Materia
from sqlalchemy.exc import IntegrityError
from modulos.central.models import Persona
from modulos.control_academico.models import Corte

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
    # Obtener materias asignadas al profesor
    materias = Materia.query.filter_by(profesor_id=cedula).all()
    # Obtener todas las materias que no están asignadas a este profesor
    materias_sin_profesor = Materia.query.filter(
        (Materia.profesor_id.is_(None)) | 
        (Materia.profesor_id != cedula)
    ).all()
    return render_template('profesores/materias.html', 
                         profesor=profesor, 
                         materias=materias, 
                         materias_sin_profesor=materias_sin_profesor)

@bp.route('/profesores/<cedula>/materias/<codigo>/asignar')
def asignar_materia_existente(cedula, codigo):
    profesor = Profesor.query.get_or_404(cedula)
    materia = Materia.query.get_or_404(codigo)
    
    # Verificar si la materia ya está asignada a este profesor
    if materia.profesor_id == cedula:
        flash('Ya tienes asignada esta materia', 'error')
        return redirect(url_for('profesores.materias_profesor', cedula=cedula))
    
    # Asignar la materia al profesor
    materia.profesor_id = cedula
    try:
        db.session.commit()
        flash('Materia asignada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al asignar la materia: {str(e)}', 'error')
    
    return redirect(url_for('profesores.materias_profesor', cedula=cedula))

@bp.route('/profesores/<cedula>/materias/<codigo>/desasignar')
def desasignar_materia(cedula, codigo):
    profesor = Profesor.query.get_or_404(cedula)
    materia = Materia.query.get_or_404(codigo)
    
    # Verificar que la materia pertenece al profesor
    if materia.profesor_id != cedula:
        flash('No tiene permiso para desasignar esta materia', 'error')
        return redirect(url_for('profesores.materias_profesor', cedula=cedula))
    
    try:
        # Desasignar la materia (establecer profesor a None)
        materia.profesor_id = None
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
    if materia.profesor_id != cedula:
        flash('No tiene permiso para eliminar esta materia', 'error')
        return redirect(url_for('profesores.materias_profesor', cedula=cedula))
    
    try:
        # Eliminar los cortes asociados primero
        Corte.query.filter_by(materia_codigo=codigo).delete()
        # Eliminar la materia
        db.session.delete(materia)
        db.session.commit()
        flash('Materia eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la materia: {str(e)}', 'error')
    
    return redirect(url_for('profesores.materias_profesor', cedula=cedula)) 