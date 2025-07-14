from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    app.config.from_object(Config)
    
    db.init_app(app)

    # Importar modelos ANTES de registrar blueprints para que SQLAlchemy los detecte
    from modulos.central.models import Persona
    from modulos.estudiantes.models import Estudiante
    from modulos.profesores.models import Profesor
    from modulos.control_academico.models import Carrera, Programa, Materia, Corte, Inscripcion, Nota
    
    # Registrar los blueprints de cada módulo
    from modulos.estudiantes import bp as estudiantes_bp
    from modulos.profesores import bp as profesores_bp
    from modulos.control_academico import bp as control_academico_bp
    from modulos.central import bp as central_bp
    
    # Configurar los blueprints con sus carpetas de plantillas
    estudiantes_bp.template_folder = 'templates'
    profesores_bp.template_folder = 'templates'
    control_academico_bp.template_folder = 'templates'
    central_bp.template_folder = 'templates'
    
    app.register_blueprint(estudiantes_bp, url_prefix='/estudiantes')
    app.register_blueprint(profesores_bp, url_prefix='/profesores')
    app.register_blueprint(control_academico_bp, url_prefix='/control_academico')
    app.register_blueprint(central_bp, url_prefix='/central')

    # Crear tablas en la base de datos
    with app.app_context():
        db.create_all()
    
    return app 