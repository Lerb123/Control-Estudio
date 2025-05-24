from flask import render_template
from modulos.profesores import bp

@bp.route('/')
def index():
    return render_template('profesores/index.html') 