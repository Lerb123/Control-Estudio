from flask import render_template
from modulos.control_academico import bp

@bp.route('/')
def index():
    return render_template('control_academico/index.html') 