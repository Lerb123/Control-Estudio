from flask import Blueprint, render_template, request

autorizar_bp = Blueprint(
                'autorizar_bp',
                __name__,
                 template_folder='templates'
                )


@autorizar_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        return render_template('login.html', nombre=nombre)
    
@autorizar_bp.route("/logout")
def logout():
    pass