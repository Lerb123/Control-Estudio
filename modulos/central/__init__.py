from flask import Blueprint

bp = Blueprint('central', __name__,
               template_folder='templates',
               static_folder='static')

from modulos.central import routes 