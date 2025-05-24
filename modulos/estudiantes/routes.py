from flask import render_template
from modulos.estudiantes import bp

@bp.route('/')
def index():
    return render_template('estudiantes/index.html') 