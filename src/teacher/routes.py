from flask import Blueprint

estudiante_bp = Blueprint("estudiante", __name__)

@estudiante_bp.route("/comprobante")
def cargar_comprobante():
    pass

@estudiante_bp.route("/materias/notas")
def visualizar_notas():
    pass

@estudiante_bp.route("/materias")
def visualizar_materias_aprobadas():
    pass
          