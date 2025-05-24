from flask import Blueprint

bp = Blueprint('estudiantes', __name__)

from modulos.estudiantes import routes 