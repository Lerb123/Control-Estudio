from flask import render_template, request, redirect, url_for, flash, session
from modulos.central import bp
from modulos.estudiantes.models import Estudiante
from modulos.central.models import Persona
from modulos.profesores.models import Profesor
from modulos import db

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasenia = request.form['contrasenia']
        persona = Persona.query.filter_by(usuario=usuario).first()
        if persona and persona.contrasenia == contrasenia:
            # Guardar datos en sesión
            session['usuario'] = persona.usuario
            session['cedula'] = persona.cedula
            session['rol'] = persona.rol
            flash(f'Bienvenido, {persona.nombre}!', 'success')
            # Redirigir según el rol
            if persona.rol == 'administrador':
                return redirect(url_for('central.index'))  # O dashboard de admin
            elif persona.rol == 'profesor':
                # Redirección directa a materias del profesor
                return redirect(url_for('profesores.materias_profesor', cedula=persona.cedula))
            elif persona.rol == 'estudiante':
                # Redirección directa a inscripciones del estudiante    
                return redirect(url_for('estudiantes.inscripciones', cedula=persona.cedula))
            else:
                flash('Rol no reconocido.', 'danger')
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('central/index.html')

@bp.route('/registrar_admin', methods=['GET', 'POST'])
def registrar_admin():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        cedula = request.form['cedula']
        telefono = request.form['telefono']
        correo = request.form['correo']
        usuario = request.form['usuario']
        contrasenia = request.form['contrasenia']
        contrasenia2 = request.form['contrasenia2']

        # Validaciones
        if contrasenia != contrasenia2:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('central/registro_admin.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=telefono, correo=correo, usuario=usuario)
        if Persona.query.filter_by(cedula=cedula).first():
            flash('Ya existe un usuario con esa cédula.', 'danger')
            return render_template('central/registro_admin.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=telefono, correo=correo, usuario=usuario)
        if Persona.query.filter_by(usuario=usuario).first():
            flash('Ya existe un usuario con ese nombre.', 'danger')
            return render_template('central/registro_admin.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=telefono, correo=correo, usuario=usuario)
        if Persona.query.filter_by(correo_electronico=correo).first():
            flash('Ya existe un usuario con ese correo electrónico.', 'danger')
            return render_template('central/registro_admin.html', nombre=nombre, apellido=apellido, cedula=cedula, telefono=telefono, correo=correo, usuario=usuario)

        # Crear el administrador
        admin = Persona(
            cedula=cedula,
            nombre=nombre,
            apellido=apellido,
            numero_telefono=telefono,
            correo_electronico=correo,
            usuario=usuario,
            contrasenia=contrasenia,
            rol='administrador'
        )
        db.session.add(admin)
        db.session.commit()
        flash('Administrador registrado exitosamente.', 'success')
        return redirect(url_for('central.index'))

    return render_template('central/registro_admin.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('central.index'))