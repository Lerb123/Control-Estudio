from flask import render_template, redirect, url_for, flash, request
from modulos.control_academico import bp
from modulos import db
from modulos.control_academico.models import Materia, Corte
from modulos.profesores.models import Profesor
from sqlalchemy.exc import IntegrityError

@bp.route('/')
def index():
    return redirect(url_for('control_academico.listar_materias'))

@bp.route('/materias')
def listar_materias():
    materias = Materia.query.all()
    profesores = Profesor.query.all()
    return render_template('control_academico/materias.html', materias=materias, profesores=profesores)

@bp.route('/materias/crear', methods=['POST'])
def crear_materia():
    codigo = request.form['codigo']
    nombre = request.form['nombre']
    profesor = request.form['profesor']
    
    # Verificar si la materia ya existe
    materia_existente = Materia.query.filter_by(codigo=codigo).first()
    if materia_existente:
        flash('Ya existe una materia con ese código.', 'error')
        return redirect(url_for('control_academico.listar_materias'))
    
    try:
        nueva_materia = Materia(
            codigo=codigo,
            nombre=nombre,
            profesor=profesor
        )
        db.session.add(nueva_materia)
        db.session.commit()
        flash('Materia creada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear la materia: {str(e)}', 'error')
    
    return redirect(url_for('control_academico.listar_materias'))

@bp.route('/materias/editar/<codigo>', methods=['GET', 'POST'])
def editar_materia(codigo):
    materia = Materia.query.get_or_404(codigo)
    profesores = Profesor.query.all()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        profesor = request.form['profesor']
        
        try:
            materia.nombre = nombre
            materia.profesor = profesor
            db.session.commit()
            flash('Materia actualizada exitosamente', 'success')
            return redirect(url_for('control_academico.listar_materias'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la materia: {str(e)}', 'error')
    
    return render_template('control_academico/editar_materia.html', materia=materia, profesores=profesores)

@bp.route('/materias/eliminar/<codigo>')
def eliminar_materia(codigo):
    materia = Materia.query.get_or_404(codigo)
    
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
    
    return redirect(url_for('control_academico.listar_materias')) 