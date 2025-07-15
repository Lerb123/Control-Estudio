from modulos.central.models import Persona
from modulos import db 

class Estudiante(Persona):

    __tablename__ = 'estudiantes'
    
    cedula = db.Column(db.String(20), db.ForeignKey('personas.cedula'), primary_key=True)
    carrera_id = db.Column(db.Integer, db.ForeignKey('carreras.id'), nullable=True)
    solvente = db.Column(db.Boolean, default = False)
    saldo_disponible = db.Column(db.Float, default=0.0)


    # Relaciones
    carrera = db.relationship('Carrera', back_populates='estudiantes')
    inscripciones = db.relationship('Inscripcion', back_populates='estudiante', cascade="all, delete-orphan")
    notas = db.relationship('Nota', back_populates='estudiante', cascade="all, delete-orphan")

    __mapper_args__ = {
        'polymorphic_identity': 'estudiante',
    }

    def __init__(self, cedula, nombre, apellido, numero_telefono, correo_electronico, usuario, contrasenia, rol, carrera_id=None, solvente=False, saldo_disponible = 0.0 ):
        super().__init__(cedula, nombre, apellido, numero_telefono, correo_electronico, usuario, contrasenia, rol)
        self.carrera_id = carrera_id
        self.solvente = solvente
        self.saldo_disponible = saldo_disponible

    def __repr__(self):
        return f'<Estudiante {self.cedula}>'

