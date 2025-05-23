from flask import Flask, render_template
from .autorizacion.routes import autorizar_bp

app = Flask(__name__)

app.register_blueprint(autorizar_bp, url_prefix='/autorizacion')

@app.route('/')
def home():
    return render_template('general.html')

if __name__ == '__main__':
    app.run(debug=True)
