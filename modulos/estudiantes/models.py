from modulos.central.models import Persona
from modulos import db 

class Estudiante(Persona):

    __tablename__ = 'estudiantes'
    
    cedula = db.Column(db.String(20), db.ForeignKey('personas.cedula'), primary_key=True)
    carrera = db.Column(db.String(100), nullable=False)
    solvente = db.Column(db.Boolean, default = False)
    notas = db.relationship('Nota', backref='estudiante', lazy=True, 
                          cascade='all, delete-orphan')

    __mapper_args__ = {
        'polymorphic_identity': 'estudiante',
    }


    def __init__(self, cedula, nombre, apellido, numero_telefono, correo_electronico, usuario, contrasenia, rol, carrera, solvente):
        super().__init__(cedula, nombre, apellido, numero_telefono, correo_electronico, usuario, contrasenia, rol)
        self.carrera = carrera
        self.solvente = solvente


    def __repr__(self):
        return f'<Estudiante {self.cedula}>'


class Nota(db.Model):
    __tablename__ = 'notas'
    
    id = db.Column(db.Integer, primary_key=True)
    estudiante_cedula = db.Column(db.String(20), db.ForeignKey('estudiantes.cedula'))
    materia = db.Column(db.String(100))
    calificacion = db.Column(db.Float)
    fecha = db.Column(db.DateTime)

    def __init__(self, estudiante_cedula, materia, calificacion, fecha):
        self.estudiante_cedula = estudiante_cedula
        self.materia = materia
        self.calificacion = calificacion
        self.fecha = fecha
    
    def __repr__(self):
        return f'<Nota {self.materia} {self.calificacion}>'