from flask import Blueprint

autorizar_bp = Blueprint("autorizacion", __name__)

@autorizar_bp.route("/login")
def login():
    pass
    
@autorizar_bp.route("/logout")
def logout():
    pass