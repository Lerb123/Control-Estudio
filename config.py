import os

class Config:
    SECRET_KEY = 'clave-secreta-para-control-de-estudios'
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'Database', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
