from flask import render_template, redirect, url_for, flash, request
from modulos.control_academico import bp
from modulos import db
from modulos.control_academico.models import (
    Carrera, Programa, Materia, Corte, Inscripcion, Nota
)
from modulos.profesores.models import Profesor
from modulos.estudiantes.models import Estudiante
from sqlalchemy.exc import IntegrityError
from datetime import datetime

# ============================================================================
# VISTA PRINCIPAL - INDEX
# ============================================================================

@bp.route('/')
def index():
    """Vista principal del módulo de control académico"""
    # Obtener estadísticas básicas
    total_carreras = Carrera.query.count()
    total_programas = Programa.query.count()
    total_materias = Materia.query.count()
    total_cortes = Corte.query.count()
    total_inscripciones = Inscripcion.query.count()
    total_notas = Nota.query.count()
    
    return render_template('control_academico/index.html', 
                         total_carreras=total_carreras,
                         total_programas=total_programas,
                         total_materias=total_materias,
                         total_cortes=total_cortes,
                         total_inscripciones=total_inscripciones,
                         total_notas=total_notas)

# ============================================================================
# CRUD CARRERAS
# ============================================================================

@bp.route('/carreras')
def listar_carreras():
    """Listar todas las carreras"""
    carreras = Carrera.query.all()
    return render_template('control_academico/carreras.html', carreras=carreras)

@bp.route('/carreras/crear', methods=['GET', 'POST'])
def crear_carrera():
    """Crear una nueva carrera"""
    if request.method == 'POST':
        nombre = request.form['nombre']
        
        # Verificar si la carrera ya existe
        carrera_existente = Carrera.query.filter_by(nombre=nombre).first()
        if carrera_existente:
            flash('Ya existe una carrera con ese nombre.', 'error')
            return redirect(url_for('control_academico.listar_carreras'))
        
        try:
            nueva_carrera = Carrera(nombre=nombre)
            db.session.add(nueva_carrera)
            db.session.commit()
            flash('Carrera creada exitosamente', 'success')
            return redirect(url_for('control_academico.listar_carreras'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la carrera: {str(e)}', 'error')
    
    return render_template('control_academico/crear_carrera.html')

@bp.route('/carreras/editar/<int:id>', methods=['GET', 'POST'])
def editar_carrera(id):
    """Editar una carrera existente"""
    carrera = Carrera.query.get_or_404(id)
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        
        try:
            carrera.nombre = nombre
            db.session.commit()
            flash('Carrera actualizada exitosamente', 'success')
            return redirect(url_for('control_academico.listar_carreras'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la carrera: {str(e)}', 'error')
    
    return render_template('control_academico/editar_carrera.html', carrera=carrera)

@bp.route('/carreras/eliminar/<int:id>')
def eliminar_carrera(id):
    """Eliminar una carrera"""
    carrera = Carrera.query.get_or_404(id)
    
    try:
        db.session.delete(carrera)
        db.session.commit()
        flash('Carrera eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la carrera: {str(e)}', 'error')
    
    return redirect(url_for('control_academico.listar_carreras'))

# ============================================================================
# CRUD PROGRAMAS
# ============================================================================

@bp.route('/programas')
def listar_programas():
    """Listar todos los programas"""
    programas = Programa.query.all()
    carreras = Carrera.query.all()
    return render_template('control_academico/programas.html', 
                         programas=programas, carreras=carreras)

@bp.route('/programas/crear', methods=['GET', 'POST'])
def crear_programa():
    """Crear un nuevo programa"""
    if request.method == 'POST':
        nombre = request.form['nombre']
        carrera_id = request.form['carrera_id']
        
        try:
            nuevo_programa = Programa(nombre=nombre, carrera_id=carrera_id)
            db.session.add(nuevo_programa)
            db.session.commit()
            flash('Programa creado exitosamente', 'success')
            return redirect(url_for('control_academico.listar_programas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el programa: {str(e)}', 'error')
    
    carreras = Carrera.query.all()
    return render_template('control_academico/crear_programa.html', carreras=carreras)

@bp.route('/programas/editar/<int:id>', methods=['GET', 'POST'])
def editar_programa(id):
    """Editar un programa existente"""
    programa = Programa.query.get_or_404(id)
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        carrera_id = request.form['carrera_id']
        
        try:
            programa.nombre = nombre
            programa.carrera_id = carrera_id
            db.session.commit()
            flash('Programa actualizado exitosamente', 'success')
            return redirect(url_for('control_academico.listar_programas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el programa: {str(e)}', 'error')
    
    carreras = Carrera.query.all()
    return render_template('control_academico/editar_programa.html', 
                         programa=programa, carreras=carreras)

@bp.route('/programas/eliminar/<int:id>')
def eliminar_programa(id):
    """Eliminar un programa"""
    programa = Programa.query.get_or_404(id)
    
    try:
        db.session.delete(programa)
        db.session.commit()
        flash('Programa eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el programa: {str(e)}', 'error')
    
    return redirect(url_for('control_academico.listar_programas'))

# ============================================================================
# CRUD MATERIAS
# ============================================================================


@bp.route('/materias')
def listar_materias():
    """Listar todas las materias"""
    materias = Materia.query.all()
    profesores = Profesor.query.all()
    programas = Programa.query.all()
    return render_template('control_academico/materias.html', 
                         materias=materias, profesores=profesores, programas=programas)

@bp.route('/materias/crear', methods=['GET', 'POST'])
def crear_materia():
    """Crear una nueva materia"""
    if request.method == 'POST':
        codigo = request.form['codigo']
        nombre = request.form['nombre']
        programa_id = request.form['programa_id']
        profesor_id = request.form.get('profesor_id') or None
        
        # Verificar si la materia ya existe
        materia_existente = Materia.query.filter_by(codigo=codigo).first()
        if materia_existente:
            flash('Ya existe una materia con ese código.', 'error')
            return redirect(url_for('control_academico.listar_materias'))
        
        try:
            nueva_materia = Materia(
                codigo=codigo,
                nombre=nombre,
                programa_id=programa_id,
                profesor_id=profesor_id
            )
            db.session.add(nueva_materia)
            db.session.commit()
            flash('Materia creada exitosamente', 'success')
            return redirect(url_for('control_academico.listar_materias'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la materia: {str(e)}', 'error')
    
    profesores = Profesor.query.all()
    programas = Programa.query.all()
    return render_template('control_academico/crear_materia.html', 
                         profesores=profesores, programas=programas)

@bp.route('/materias/editar/<int:codigo>', methods=['GET', 'POST'])
def editar_materia(codigo):
    """Editar una materia existente"""
    materia = Materia.query.get_or_404(codigo)
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        programa_id = request.form['programa_id']
        profesor_id = request.form.get('profesor_id') or None
        
        try:
            materia.nombre = nombre
            materia.programa_id = programa_id
            materia.profesor_id = profesor_id
            db.session.commit()
            flash('Materia actualizada exitosamente', 'success')
            return redirect(url_for('control_academico.listar_materias'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la materia: {str(e)}', 'error')
    
    profesores = Profesor.query.all()
    programas = Programa.query.all()
    return render_template('control_academico/editar_materia.html', 
                         materia=materia, profesores=profesores, programas=programas)

@bp.route('/materias/eliminar/<int:codigo>')
def eliminar_materia(codigo):
    """Eliminar una materia"""
    materia = Materia.query.get_or_404(codigo)
    
    try:
        db.session.delete(materia)
        db.session.commit()
        flash('Materia eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la materia: {str(e)}', 'error')
    
    return redirect(url_for('control_academico.listar_materias'))

# ============================================================================
# CRUD CORTES
# ============================================================================

@bp.route('/cortes')
def listar_cortes():
    """Listar todos los cortes"""
    cortes = Corte.query.all()
    programas = Programa.query.all()
    return render_template('control_academico/cortes.html', 
                         cortes=cortes, programas=programas)

@bp.route('/cortes/crear', methods=['GET', 'POST'])
def crear_corte():
    """Crear un nuevo corte"""
    if request.method == 'POST':
        programa_id = request.form['programa_id']
        seccion = request.form['seccion']
        zona = request.form['zona']
        fecha_inicio = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d').date()
        
        try:
            nuevo_corte = Corte(
                programa_id=programa_id,
                seccion=seccion,
                zona=zona,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            db.session.add(nuevo_corte)
            db.session.commit()
            flash('Corte creado exitosamente', 'success')
            return redirect(url_for('control_academico.listar_cortes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el corte: {str(e)}', 'error')
    
    programas = Programa.query.all()
    return render_template('control_academico/crear_corte.html', programas=programas)

@bp.route('/cortes/editar/<int:id>', methods=['GET', 'POST'])
def editar_corte(id):
    """Editar un corte existente"""
    corte = Corte.query.get_or_404(id)
    
    if request.method == 'POST':
        programa_id = request.form['programa_id']
        seccion = request.form['seccion']
        zona = request.form['zona']
        fecha_inicio = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d').date()
        
        try:
            corte.programa_id = programa_id
            corte.seccion = seccion
            corte.zona = zona
            corte.fecha_inicio = fecha_inicio
            corte.fecha_fin = fecha_fin
            db.session.commit()
            flash('Corte actualizado exitosamente', 'success')
            return redirect(url_for('control_academico.listar_cortes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el corte: {str(e)}', 'error')
    
    programas = Programa.query.all()
    return render_template('control_academico/editar_corte.html', 
                         corte=corte, programas=programas)

@bp.route('/cortes/eliminar/<int:id>')
def eliminar_corte(id):
    """Eliminar un corte"""
    corte = Corte.query.get_or_404(id)
    
    try:
        db.session.delete(corte)
        db.session.commit()
        flash('Corte eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el corte: {str(e)}', 'error')
    
    return redirect(url_for('control_academico.listar_cortes'))

# ============================================================================
# CRUD INSCRIPCIONES
# ============================================================================

@bp.route('/inscripciones')
def listar_inscripciones():
    """Listar todas las inscripciones"""
    inscripciones = Inscripcion.query.all()
    estudiantes = Estudiante.query.all()
    cortes = Corte.query.all()
    return render_template('control_academico/inscripciones.html', 
                         inscripciones=inscripciones, 
                         estudiantes=estudiantes, 
                         cortes=cortes)

@bp.route('/inscripciones/crear', methods=['GET', 'POST'])
def crear_inscripcion():
    """Crear una nueva inscripción"""
    if request.method == 'POST':
        estudiante_id = request.form['estudiante_id']
        corte_id = request.form['corte_id']
        estado_pago = 'estado_pago' in request.form
        
        try:
            nueva_inscripcion = Inscripcion(
                estudiante_id=estudiante_id,
                corte_id=corte_id,
                estado_pago=estado_pago
            )
            db.session.add(nueva_inscripcion)
            db.session.commit()
            flash('Inscripción creada exitosamente', 'success')
            return redirect(url_for('control_academico.listar_inscripciones'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la inscripción: {str(e)}', 'error')
    
    estudiantes = Estudiante.query.all()
    cortes = Corte.query.all()
    return render_template('control_academico/crear_inscripcion.html', 
                         estudiantes=estudiantes, cortes=cortes)

@bp.route('/inscripciones/editar/<int:id>', methods=['GET', 'POST'])
def editar_inscripcion(id):
    """Editar una inscripción existente"""
    inscripcion = Inscripcion.query.get_or_404(id)
    
    if request.method == 'POST':
        estudiante_id = request.form['estudiante_id']
        corte_id = request.form['corte_id']
        estado_pago = 'estado_pago' in request.form
        
        try:
            inscripcion.estudiante_id = estudiante_id
            inscripcion.corte_id = corte_id
            inscripcion.estado_pago = estado_pago
            db.session.commit()
            flash('Inscripción actualizada exitosamente', 'success')
            return redirect(url_for('control_academico.listar_inscripciones'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la inscripción: {str(e)}', 'error')
    
    estudiantes = Estudiante.query.all()
    cortes = Corte.query.all()
    return render_template('control_academico/editar_inscripcion.html', 
                         inscripcion=inscripcion, 
                         estudiantes=estudiantes, 
                         cortes=cortes)

@bp.route('/inscripciones/eliminar/<int:id>')
def eliminar_inscripcion(id):
    """Eliminar una inscripción"""
    inscripcion = Inscripcion.query.get_or_404(id)
    
    try:
        db.session.delete(inscripcion)
        db.session.commit()
        flash('Inscripción eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la inscripción: {str(e)}', 'error')
    
    return redirect(url_for('control_academico.listar_inscripciones'))

# ============================================================================
# CRUD NOTAS
# ============================================================================

@bp.route('/notas')
def listar_notas():
    """Listar todas las notas"""
    notas = Nota.query.all()
    estudiantes = Estudiante.query.all()
    materias = Materia.query.all()
    return render_template('control_academico/notas.html', 
                         notas=notas, 
                         estudiantes=estudiantes, 
                         materias=materias)

@bp.route('/notas/crear', methods=['GET', 'POST'])
def crear_nota():
    """Crear una nueva nota"""
    if request.method == 'POST':
        estudiante_id = request.form['estudiante_id']
        materia_codigo = request.form['materia_codigo']
        nota = float(request.form['nota'])
        
        try:
            nueva_nota = Nota(
                estudiante_id=estudiante_id,
                materia_codigo=materia_codigo,
                nota=nota
            )
            db.session.add(nueva_nota)
            db.session.commit()
            flash('Nota creada exitosamente', 'success')
            return redirect(url_for('control_academico.listar_notas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la nota: {str(e)}', 'error')
    
    estudiantes = Estudiante.query.all()
    materias = Materia.query.all()
    return render_template('control_academico/crear_nota.html', 
                         estudiantes=estudiantes, materias=materias)

@bp.route('/notas/editar/<int:id>', methods=['GET', 'POST'])
def editar_nota(id):
    """Editar una nota existente"""
    nota = Nota.query.get_or_404(id)
    
    if request.method == 'POST':
        estudiante_id = request.form['estudiante_id']
        materia_codigo = request.form['materia_codigo']
        valor_nota = float(request.form['nota'])
        
        try:
            nota.estudiante_id = estudiante_id
            nota.materia_codigo = materia_codigo
            nota.nota = valor_nota
            db.session.commit()
            flash('Nota actualizada exitosamente', 'success')
            return redirect(url_for('control_academico.listar_notas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la nota: {str(e)}', 'error')
    
    estudiantes = Estudiante.query.all()
    materias = Materia.query.all()
    return render_template('control_academico/editar_nota.html', 
                         nota=nota, 
                         estudiantes=estudiantes, 
                         materias=materias)

@bp.route('/notas/eliminar/<int:id>')
def eliminar_nota(id):
    """Eliminar una nota"""
    nota = Nota.query.get_or_404(id)
    
    try:
        db.session.delete(nota)
        db.session.commit()
        flash('Nota eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la nota: {str(e)}', 'error')
    
    return redirect(url_for('control_academico.listar_notas')) 