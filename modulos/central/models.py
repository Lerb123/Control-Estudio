from modulos import db

class Persona(db.Model):
    __tablename__ = 'personas'
    
    # Usamos la cédula como primary key
    cedula = db.Column(db.String(20), primary_key=True, unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    numero_telefono = db.Column(db.Integer)
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

class ControlEstudios(db.Model):
    __tablename__ = 'control_estudios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_institucion = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    telefono = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    rector = db.Column(db.String(100), nullable=False)
    fecha_fundacion = db.Column(db.Date, nullable=False)
    tipo_institucion = db.Column(db.String(50), nullable=False)  # Pública, Privada, etc.
    estado = db.Column(db.Boolean, default=True)  # Activa/Inactiva
    
    def __init__(self, nombre_institucion, direccion, telefono, email, rector, fecha_fundacion, tipo_institucion, estado=True):
        self.nombre_institucion = nombre_institucion
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.rector = rector
        self.fecha_fundacion = fecha_fundacion
        self.tipo_institucion = tipo_institucion
        self.estado = estado
    
    def __repr__(self):
        return f'<ControlEstudios {self.nombre_institucion}>'