from flask import Blueprint

bp = Blueprint('profesores', __name__, 
               url_prefix='/profesores',
               template_folder='templates')

from . import routes 