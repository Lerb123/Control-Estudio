from flask import render_template, redirect, url_for, flash, request
from modulos.estudiantes import bp
from modulos import db
from modulos.estudiantes.models import Estudiante
from modulos.control_academico.models import Materia, Corte, Inscripcion
from datetime import datetime

@bp.route('/')
def index():
    estudiantes = Estudiante.query.all()
    return render_template('estudiantes/listar_estudiantes.html', estudiantes=estudiantes) 

@bp.route('/registro_estudiantes',methods =['GET','POST'])
def nuevo_estudiante():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        cedula = request.form['cedula']
        numero_telefono = request.form['telefono']
        correo_electronico = request.form['correo']
        usuario = request.form['usuario']
        carrera = request.form['carrera']
        solvente = bool(request.form.get('solvente', False))
        contrasenia = cedula
        rol = 'estudiante'

        # Validación de cédula
        if not cedula.isdigit() or len(cedula) < 8:
            flash('La cédula debe contener al menos 8 dígitos y solo números.', 'error')
            return render_template('estudiantes/form_estudiante.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=numero_telefono, correo=correo_electronico, usuario=usuario, carrera=carrera)

        if Estudiante.query.filter_by(cedula=cedula).first():
            flash('Ya existe un estudiante con esa cédula.', 'error')
            return render_template('estudiantes/form_estudiante.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=numero_telefono, correo=correo_electronico, usuario=usuario, carrera=carrera)
        if Estudiante.query.filter_by(usuario=usuario).first():
            flash('Ya existe un estudiante con ese nombre de usuario.', 'error')
            return render_template('estudiantes/form_estudiante.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=numero_telefono, correo=correo_electronico, usuario=usuario, carrera=carrera)
        if Estudiante.query.filter_by(correo_electronico=correo_electronico).first():
            flash('Ya existe un estudiante con ese correo electrónico.', 'error')
            return render_template('estudiantes/form_estudiante.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=numero_telefono, correo=correo_electronico, usuario=usuario, carrera=carrera)

        estudiante = Estudiante(cedula, nombre, apellido, numero_telefono, correo_electronico, usuario, contrasenia, rol, carrera, solvente)
        db.session.add(estudiante)
        db.session.commit()

        flash('Estudiate registrado exitosamente', 'success')
        return redirect(url_for('estudiantes.index'))
    
    return render_template('estudiantes/form_estudiante.html')

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
            return render_template('estudiantes/form_estudiante.html', estudiante=estudiante)

        # Verificar unicidad de usuario (excluyendo el actual)
        usuario_existente = Estudiante.query.filter(
            Estudiante.usuario == nuevo_usuario,
            Estudiante.cedula != estudiante.cedula
        ).first()
        if usuario_existente:
            flash('Ya existe un estudiante con ese nombre de usuario.', 'error')
            return render_template('estudiantes/form_estudiante.html', estudiante=estudiante)

        # Verificar unicidad de correo (excluyendo el actual)
        correo_existente = Estudiante.query.filter(
            Estudiante.correo_electronico == nuevo_correo,
            Estudiante.cedula != estudiante.cedula
        ).first()
        if correo_existente:
            flash('Ya existe un estudiante con ese correo electrónico.', 'error')
            return render_template('estudiantes/form_estudiante.html', estudiante=estudiante)

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

    return render_template('estudiantes/form_estudiante.html', estudiante=estudiante)

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
            #datos de la inscripcion 
            datosMateria = request.form['materia']
            
            partes = datosMateria.split('-')
            if len(partes) != 6:
                flash('Error en el formato de los datos de la materia', 'error')
                return redirect(url_for('estudiantes.inscripciones', cedula=estudiante.cedula))
            
            codigo_corte = partes[0].strip()
            seccion = partes[1].strip()
            periodo = partes[2].strip()
            nombre = partes[3].strip()
            codigo_materia = partes[4].strip()
            profesor = partes[5].strip()

            # Verificar si la materia ya existe
            materia_existente = Materia.query.filter_by(codigo=codigo_materia).first()
            if not materia_existente:
                #creacion de materia 
                materia = Materia(codigo=codigo_materia, nombre=nombre, profesor=profesor)
                db.session.add(materia)
            
            # Verificar si el corte ya existe
            corte_existente = Corte.query.filter_by(id=codigo_corte, seccion=seccion, periodo=periodo).first()
            if not corte_existente:    
                #creacion de corte 
                corte = Corte(id=codigo_corte, materia_codigo=codigo_materia, seccion=seccion, periodo=periodo)
                db.session.add(corte)

            #verifiacr si estudiante ya esta inscrito 
            estudiante_inscrito =  Inscripcion.query.filter_by(estudiante_cedula=estudiante.cedula, corte_id=codigo_corte).first()
            if not estudiante_inscrito:
                inscripcion = Inscripcion(
                    estudiante_cedula=estudiante.cedula,
                    materia_codigo=codigo_materia,
                    corte_id=codigo_corte,
                    nota=None, 
                    fecha_inscripcion=datetime.now()
                )
                db.session.add(inscripcion)
                flash('Inscripción exitosa', 'success')
            else:
                flash('Ya estás inscrito en este corte', 'warning')

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Error al procesar la inscripción: {str(e)}', 'error')
        
        return redirect(url_for('estudiantes.inscripciones', cedula=estudiante.cedula))
    
    # Obtén todas las inscripciones del estudiante, junto con materia y corte
    inscripciones = Inscripcion.query.filter_by(estudiante_cedula=estudiante.cedula).all()
    
    # Obtener todas las materias que tienen profesor asignado
    materias_disponibles = Materia.query.filter(Materia.profesor.isnot(None)).all()
    
    return render_template('estudiantes/inscripciones.html',
                         estudiante=estudiante, 
                         inscripciones=inscripciones,
                         materias_disponibles=materias_disponibles)

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
    return redirect(url_for('estudiantes.inscripciones', cedula=inscripcion.estudiante_cedula))

