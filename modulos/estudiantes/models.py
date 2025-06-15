from modulos.central.models import Persona
from modulos.control_academico.models import Materia, Corte, Inscripcion
from modulos import db 

class Estudiante(Persona):

    __tablename__ = 'estudiantes'
    
    cedula = db.Column(db.String(20), db.ForeignKey('personas.cedula'), primary_key=True)
    carrera = db.Column(db.String(100), nullable=False)
    solvente = db.Column(db.Boolean, default = False)

    # Relación con iscripciones
    inscripciones = db.relationship('Inscripcion', back_populates='estudiante',cascade="all, delete-orphan")

    __mapper_args__ = {
        'polymorphic_identity': 'estudiante',
    }


    def __init__(self, cedula, nombre, apellido, numero_telefono, correo_electronico, usuario, contrasenia, rol, carrera, solvente):
        super().__init__(cedula, nombre, apellido, numero_telefono, correo_electronico, usuario, contrasenia, rol)
        self.carrera = carrera
        self.solvente = solvente


    def __repr__(self):
        return f'<Estudiante {self.cedula}>'
