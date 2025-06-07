from flask import Blueprint

bp = Blueprint('estudiantes', __name__ , template_folder='templates')

from modulos.estudiantes import routes 