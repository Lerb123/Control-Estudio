from flask import render_template, redirect, url_for, flash, request
from modulos.estudiantes import bp
from modulos import db
from modulos.estudiantes.models import Estudiante, Nota
from datetime import datetime

@bp.route('/')
def index():
    estudiantes = Estudiante.query.all()
    return render_template('estudiantes/index.html', estudiantes = estudiantes) 

@bp.route('/registroEstudiantes',methods =['GET','POST'])
def nuevo_estudiante():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        cedula = request.form['cedula']
        if not cedula.isdigit() or len(cedula) < 8 :
            flash('La cédula debe contener al menos 8 dígitos y solo números.', 'error')
            return redirect(url_for('estudiantes.nuevo_estudiante'))
        numero_telefono = request.form['telefono']
        correo_electronico = request.form['correo']
        usuario = request.form['usuario']
        contrasenia = cedula
        rol= 'estudiante'
        carrera = request.form['carrera']
        solvente=bool(request.form.get('solvente',False))
        
        if Estudiante.query.filter_by(cedula=cedula).first():
            flash('Ya existe un estudiante con esa cédula.', 'error')
            return redirect(url_for('estudiantes.nuevo_estudiante'))
        if Estudiante.query.filter_by(usuario=usuario).first():
            flash('Ya existe un estudiante con ese nombre de usuario.', 'error')
            return redirect(url_for('estudiantes.nuevo_estudiante'))
        if Estudiante.query.filter_by(correo_electronico=correo_electronico).first():
            flash('Ya existe un estudiante con ese correo electrónico.', 'error')
            return redirect(url_for('estudiantes.nuevo_estudiante'))

        estudiante = Estudiante(cedula,nombre,apellido,numero_telefono,correo_electronico,usuario,contrasenia,rol,carrera,solvente)
        
        db.session.add(estudiante)
        db.session.commit()

        flash('Estudiate registrado exitosamente', 'success')
        return redirect(url_for('estudiantes.index'))
        
    estudiantes = Estudiante.query.all()
    return render_template('estudiantes/registrar_estudiante.html', estudiantes=estudiantes)

@bp.route('/editar/<cedula>', methods=['GET', 'POST'])
def editar_estudiante(cedula):
    estudiante = Estudiante.query.get_or_404(cedula)
    if request.method == 'POST':
        nueva_cedula = request.form['cedula']
        nuevo_usuario = request.form['usuario']
        nuevo_correo = request.form['correo']

        # Verificar unicidad de cédula (si cambió)
        if nueva_cedula != estudiante.cedula and Estudiante.query.filter_by(cedula=nueva_cedula).first():
            flash('Ya existe un estudiante con esa cédula.', 'error')
            return render_template('estudiantes/editar_estudiante.html', estudiante=estudiante)

        # Verificar unicidad de usuario (excluyendo el actual)
        usuario_existente = Estudiante.query.filter(
            Estudiante.usuario == nuevo_usuario,
            Estudiante.cedula != estudiante.cedula
        ).first()
        if usuario_existente:
            flash('Ya existe un estudiante con ese nombre de usuario.', 'error')
            return render_template('estudiantes/editar_estudiante.html', estudiante=estudiante)

        # Verificar unicidad de correo (excluyendo el actual)
        correo_existente = Estudiante.query.filter(
            Estudiante.correo_electronico == nuevo_correo,
            Estudiante.cedula != estudiante.cedula
        ).first()
        if correo_existente:
            flash('Ya existe un estudiante con ese correo electrónico.', 'error')
            return render_template('estudiantes/editar_estudiante.html', estudiante=estudiante)

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
                carrera=request.form['carrera'],
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
        estudiante.carrera = request.form['carrera']
        db.session.commit()
        flash('Estudiante actualizado exitosamente', 'success')
        return redirect(url_for('estudiantes.index'))

    return render_template('estudiantes/editar_estudiante.html', estudiante=estudiante)

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

