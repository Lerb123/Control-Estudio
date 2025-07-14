from flask import render_template, redirect, url_for, flash, request
from modulos.estudiantes import bp
from modulos import db
from modulos.estudiantes.models import Estudiante
from modulos.control_academico.models import Materia, Corte, Inscripcion, Carrera
from datetime import datetime

@bp.route('/')
def index():
    estudiantes = Estudiante.query.all()
    return render_template('estudiantes/listar_estudiantes.html', estudiantes=estudiantes) 

@bp.route('/registro_estudiantes',methods =['GET','POST'])
def nuevo_estudiante():
    # Obtener todas las carreras disponibles
    carreras = Carrera.query.all()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        cedula = request.form['cedula']
        numero_telefono = request.form['telefono']
        correo_electronico = request.form['correo']
        usuario = request.form['usuario']
        carrera_id = request.form['carrera']
        solvente = bool(request.form.get('solvente', False))
        contrasenia = cedula
        rol = 'estudiante'

        # Validación de cédula
        if not cedula.isdigit() or len(cedula) < 8:
            flash('La cédula debe contener al menos 8 dígitos y solo números.', 'error')
            return render_template('estudiantes/form_estudiante.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=numero_telefono, correo=correo_electronico, usuario=usuario, carrera=carrera_id, carreras=carreras)

        if Estudiante.query.filter_by(cedula=cedula).first():
            flash('Ya existe un estudiante con esa cédula.', 'error')
            return render_template('estudiantes/form_estudiante.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=numero_telefono, correo=correo_electronico, usuario=usuario, carrera=carrera_id, carreras=carreras)
        if Estudiante.query.filter_by(usuario=usuario).first():
            flash('Ya existe un estudiante con ese nombre de usuario.', 'error')
            return render_template('estudiantes/form_estudiante.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=numero_telefono, correo=correo_electronico, usuario=usuario, carrera=carrera_id, carreras=carreras)
        if Estudiante.query.filter_by(correo_electronico=correo_electronico).first():
            flash('Ya existe un estudiante con ese correo electrónico.', 'error')
            return render_template('estudiantes/form_estudiante.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=numero_telefono, correo=correo_electronico, usuario=usuario, carrera=carrera_id, carreras=carreras)

        estudiante = Estudiante(cedula, nombre, apellido, numero_telefono, correo_electronico, usuario, contrasenia, rol, carrera_id, solvente)
        db.session.add(estudiante)
        db.session.commit()

        flash('Estudiate registrado exitosamente', 'success')
        return redirect(url_for('estudiantes.index'))
    
    return render_template('estudiantes/form_estudiante.html', carreras=carreras)

@bp.route('/editar/<cedula>', methods=['GET', 'POST'])
def editar_estudiante(cedula):
    estudiante = Estudiante.query.get_or_404(cedula)
    # Obtener todas las carreras disponibles
    carreras = Carrera.query.all()
    
    if request.method == 'POST':
        nueva_cedula = request.form['cedula']
        nuevo_usuario = request.form['usuario']
        nuevo_correo = request.form['correo']
        carrera_id = request.form['carrera']

        # Verificar unicidad de cédula (si cambió)
        if nueva_cedula != estudiante.cedula and Estudiante.query.filter_by(cedula=nueva_cedula).first():
            flash('Ya existe un estudiante con esa cédula.', 'error')
            return render_template('estudiantes/form_estudiante.html', estudiante=estudiante, carreras=carreras)

        # Verificar unicidad de usuario (excluyendo el actual)
        usuario_existente = Estudiante.query.filter(
            Estudiante.usuario == nuevo_usuario,
            Estudiante.cedula != estudiante.cedula
        ).first()
        if usuario_existente:
            flash('Ya existe un estudiante con ese nombre de usuario.', 'error')
            return render_template('estudiantes/form_estudiante.html', estudiante=estudiante, carreras=carreras)

        # Verificar unicidad de correo (excluyendo el actual)
        correo_existente = Estudiante.query.filter(
            Estudiante.correo_electronico == nuevo_correo,
            Estudiante.cedula != estudiante.cedula
        ).first()
        if correo_existente:
            flash('Ya existe un estudiante con ese correo electrónico.', 'error')
            return render_template('estudiantes/form_estudiante.html', estudiante=estudiante, carreras=carreras)

        # Si la cédula cambió, crear nuevo registro y borrar el anterior
        if nueva_cedula != estudiante.cedula:
            # Elimina primero el estudiante original y haz commit
            db.session.delete(estudiante)
            db.session.commit()
            # Ahora crea el nuevo estudiante
            nuevo_estudiante = Estudiante(
                cedula=nueva_cedula,
                nombre=request.form['nombre'],
                apellido=request.form['apellido'],
                numero_telefono=request.form['telefono'],
                correo_electronico=nuevo_correo,
                usuario=nuevo_usuario,
                contrasenia=nueva_cedula,
                rol='estudiante',
                carrera_id=carrera_id,
                solvente=getattr(estudiante, 'solvente', True)
            )
            db.session.add(nuevo_estudiante)
            db.session.commit()
            flash('Estudiante actualizado exitosamente (cédula cambiada)', 'success')
            return redirect(url_for('estudiantes.index'))

        # Si la cédula no cambió, solo actualiza los campos
        estudiante.nombre = request.form['nombre']
        estudiante.apellido = request.form['apellido']
        estudiante.numero_telefono = request.form['telefono']
        estudiante.correo_electronico = nuevo_correo
        estudiante.usuario = nuevo_usuario
        estudiante.contrasenia = estudiante.cedula
        estudiante.rol = 'estudiante'
        estudiante.carrera_id = carrera_id
        db.session.commit()
        flash('Estudiante actualizado exitosamente', 'success')
        return redirect(url_for('estudiantes.index'))

    return render_template('estudiantes/form_estudiante.html', estudiante=estudiante, carreras=carreras)

@bp.route('/elimnar/<cedula>')
def eliminar_estudiante(cedula):
    estudiante = Estudiante.query.get_or_404(cedula)
    try:
        db.session.delete(estudiante)
        db.session.commit()
        flash('Estudiante eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar estudiante: {str(e)}', 'danger')
    return render_template('estudiantes/index.html', estudiantes=Estudiante.query.all())

@bp.route('/inscripciones/<cedula>' , methods=['GET', 'POST'])
def inscripciones(cedula):
    estudiante = Estudiante.query.get_or_404(cedula)
    if request.method == 'POST':
        try:
            corte_id = request.form['corte']
            
            # Verificar si el estudiante ya está inscrito en este corte
            inscripcion_existente = Inscripcion.query.filter_by(
                estudiante_id=estudiante.cedula, 
                corte_id=corte_id
            ).first()
            
            if inscripcion_existente:
                flash('Ya estás inscrito en este corte', 'warning')
            else:
                # Crear nueva inscripción
                inscripcion = Inscripcion(
                    estudiante_id=estudiante.cedula,
                    corte_id=corte_id,
                    estado_pago=False
                )
                db.session.add(inscripcion)
                db.session.commit()
                flash('Inscripción exitosa', 'success')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error al procesar la inscripción: {str(e)}', 'error')
        
        return redirect(url_for('estudiantes.inscripciones', cedula=estudiante.cedula))
    
    # Obtener todas las inscripciones del estudiante
    inscripciones = Inscripcion.query.filter_by(estudiante_id=estudiante.cedula).all()
    
    # Obtener todos los cortes disponibles
    cortes_disponibles = Corte.query.all()
    
    return render_template('estudiantes/inscripciones.html',
                         estudiante=estudiante, 
                         inscripciones=inscripciones,
                         cortes_disponibles=cortes_disponibles)

@bp.route('/eliminar_inscripcion/<int:inscripcion_id>')
def eliminar_inscripcion(inscripcion_id):
    inscripcion = Inscripcion.query.get_or_404(inscripcion_id)
    try:
        db.session.delete(inscripcion)
        db.session.commit()
        flash('Inscripción eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar inscripción: {str(e)}', 'danger')
    return redirect(url_for('estudiantes.inscripciones', cedula=inscripcion.estudiante_id))

