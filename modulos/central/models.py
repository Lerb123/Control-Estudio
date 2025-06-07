from modulos import db

class Persona(db.Model):
    __tablename__ = 'personas'
    
    # Usamos la cédula como primary key
    cedula = db.Column(db.String(20), primary_key=True,unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    numero_telefono = db.Column(db.String(20))
    correo_electronico = db.Column(db.String(100), unique=True, nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    contrasenia = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), nullable=False)

    
    __mapper_args__ = {
        'polymorphic_identity': 'persona',
        'polymorphic_on': rol
    }

    def __init__(self, cedula, nombre, apellido, numero_telefono, correo_electronico, usuario, contrasenia, rol):
        self.cedula = cedula
        self.nombre = nombre
        self.apellido = apellido
        self.numero_telefono = numero_telefono
        self.correo_electronico = correo_electronico
        self.usuario = usuario
        self.contrasenia = contrasenia
        self.rol = rol

    def __repr__(self):
        return f'<Persona {self.cedula}>'