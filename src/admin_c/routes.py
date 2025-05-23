from flask import Blueprint
admin_bp = Blueprint("administrador", __name__)



@admin_bp.route("/crear_alumno")
def crear_alumno():
    pass

@admin_bp.route("/crear_materia")
def crear_materia():
    pass
      
@admin_bp.route("/crear_profesor")
def crear_profesor():
    pass
    
@admin_bp.route("/crear_programa")
def crear_programa():
    pass