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
    
    # Registrar los blueprints de cada módulo
    from modulos.estudiantes import bp as estudiantes_bp
    from modulos.profesores import bp as profesores_bp
    from modulos.control_academico import bp as control_academico_bp
    from modulos.central import bp as central_bp
    
    app.register_blueprint(estudiantes_bp, url_prefix='/estudiantes')
    app.register_blueprint(profesores_bp, url_prefix='/profesores')
    app.register_blueprint(control_academico_bp, url_prefix='/control-academico')
    app.register_blueprint(central_bp, url_prefix='/central')
    
    return app 