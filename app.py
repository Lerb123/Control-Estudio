from modulos import create_app, db
from flask import redirect, url_for
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

@app.route('/')
def index():
    return redirect(url_for('central.index'))

if __name__ == '__main__':
    app.run(debug=True)