from flask import Blueprint

bp = Blueprint('control_academico', __name__)

from modulos.control_academico import routes 