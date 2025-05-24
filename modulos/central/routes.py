from flask import render_template
from modulos.central import bp

@bp.route('/')
def index():
    return render_template('central/index.html') 