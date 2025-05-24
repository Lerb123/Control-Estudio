import os

class Config:
    SECRET_KEY = 'clave-secreta-para-control-de-estudios'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
