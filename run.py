from flask import Flask, render_template


app = Flask(__name__)

# ruta de prueba
@app.route('/')
def home():
    return render_template('general.html')

