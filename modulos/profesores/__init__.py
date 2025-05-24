from flask import Blueprint

bp = Blueprint('profesores', __name__)

from modulos.profesores import routes 