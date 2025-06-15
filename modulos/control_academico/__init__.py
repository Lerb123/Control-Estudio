from flask import Blueprint

bp = Blueprint('control_academico', __name__, 
               template_folder='templates',
               static_folder='static')

from modulos.control_academico import routes 