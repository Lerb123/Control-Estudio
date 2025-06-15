from modulos.central.models import Persona
from modulos.control_academico.models import Materia
from modulos import db

class Profesor(Persona):
    __tablename__ = 'profesores'
    
    cedula = db.Column(db.String(20), db.ForeignKey('personas.cedula'), primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)

    # Relación con materias
    materias = db.relationship('Materia', 
                             backref='profesor_info',
                             primaryjoin="Profesor.cedula==Materia.profesor",
                             foreign_keys=[Materia.profesor])

    __mapper_args__ = {
        'polymorphic_identity': 'profesor',
    }

    def __init__(self, cedula, nombre, apellido, numero_telefono, correo_electronico, usuario, contrasenia, rol, titulo):
        super().__init__(cedula, nombre, apellido, numero_telefono, correo_electronico, usuario, contrasenia, rol)
        self.titulo = titulo

    def __repr__(self):
        return f'<Profesor {self.nombre} {self.apellido}>' 