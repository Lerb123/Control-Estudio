from modulos import db
from datetime import datetime

class Carrera(db.Model):
    __tablename__ = 'carreras'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relaciones
    programas = db.relationship('Programa', back_populates='carrera')
    estudiantes = db.relationship('Estudiante', back_populates='carrera')
    
    def __init__(self, nombre):
        self.nombre = nombre
    
    def __repr__(self):
        return f'<Carrera {self.nombre}>'

class Programa(db.Model):
    __tablename__ = 'programas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    carrera_id = db.Column(db.Integer, db.ForeignKey('carreras.id'), nullable=False)
    
    # Relaciones
    carrera = db.relationship('Carrera', back_populates='programas')
    materias = db.relationship('Materia', back_populates='programa')
    cortes = db.relationship('Corte', back_populates='programa')
    
    def __init__(self, nombre, carrera_id):
        self.nombre = nombre
        self.carrera_id = carrera_id
    
    def __repr__(self):
        return f'<Programa {self.nombre}>'

class Materia(db.Model):
    __tablename__ ='materias'

    codigo = db.Column(db.Integer, primary_key=True, unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    programa_id = db.Column(db.Integer, db.ForeignKey('programas.id'), nullable=False)
    
    # Relaciones
    programa = db.relationship('Programa', back_populates='materias')
    asignaciones = db.relationship('AsignacionMateria', back_populates='materia')
    notas = db.relationship('Nota', back_populates='materia')
    
    def __init__(self, codigo, nombre, programa_id):
        self.codigo = codigo
        self.nombre = nombre
        self.programa_id = programa_id
    
    def __repr__(self):
        return f'<Materia {self.codigo} - {self.nombre}>'

class Corte(db.Model):
    __tablename__ = 'cortes'
    
    id = db.Column(db.Integer, primary_key=True)
    programa_id = db.Column(db.Integer, db.ForeignKey('programas.id'), nullable=False)
    seccion = db.Column(db.String(20), nullable=False)
    zona = db.Column(db.String(50), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    
    # Relaciones
    programa = db.relationship('Programa', back_populates='cortes')
    inscripciones = db.relationship('Inscripcion', back_populates='corte')
    asignaciones = db.relationship('AsignacionMateria', back_populates='corte')
    
    def __init__(self, programa_id, seccion, zona, fecha_inicio, fecha_fin):
        self.programa_id = programa_id
        self.seccion = seccion
        self.zona = zona
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
    
    def __repr__(self):
        return f'<Corte {self.seccion} - {self.zona} - {self.programa.nombre} - {self.fecha_inicio} - {self.fecha_fin}>'

class AsignacionMateria(db.Model):
    __tablename__ = 'asignaciones_materias'
    
    id = db.Column(db.Integer, primary_key=True)
    profesor_id = db.Column(db.String(20), db.ForeignKey('profesores.cedula'), nullable=False)
    materia_codigo = db.Column(db.Integer, db.ForeignKey('materias.codigo'), nullable=False)
    corte_id = db.Column(db.Integer, db.ForeignKey('cortes.id'), nullable=False)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    profesor = db.relationship('Profesor', back_populates='asignaciones')
    materia = db.relationship('Materia', back_populates='asignaciones')
    corte = db.relationship('Corte', back_populates='asignaciones')
    
    # Restricción única: un profesor solo puede ser asignado a una combinación única de corte-materia
    __table_args__ = (
        db.UniqueConstraint('materia_codigo', 'corte_id', name='uq_materia_corte'),
    )
    
    def __init__(self, profesor_id, materia_codigo, corte_id):
        self.profesor_id = profesor_id
        self.materia_codigo = materia_codigo
        self.corte_id = corte_id
    
    def __repr__(self):
        return f'<AsignacionMateria Profesor: {self.profesor_id} - Materia: {self.materia_codigo} - Corte: {self.corte_id}>'

class Inscripcion(db.Model):
    __tablename__ = 'inscripciones'
    
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.String(20), db.ForeignKey('estudiantes.cedula'), nullable=False)
    corte_id = db.Column(db.Integer, db.ForeignKey('cortes.id'), nullable=False)
    fecha_inscripcion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    estado_pago = db.Column(db.Boolean, default=False)
    
    # Relaciones
    estudiante = db.relationship('Estudiante', back_populates='inscripciones')
    corte = db.relationship('Corte', back_populates='inscripciones')
    
    def __init__(self, estudiante_id, corte_id, estado_pago=False):
        self.estudiante_id = estudiante_id
        self.corte_id = corte_id
        self.estado_pago = estado_pago
    
    def __repr__(self):
        return f'<Inscripcion {self.id} - Estudiante: {self.estudiante_id} - Corte: {self.corte_id}>'

class Nota(db.Model):
    __tablename__ = 'notas'
    
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.String(20), db.ForeignKey('estudiantes.cedula'), nullable=False)
    materia_codigo = db.Column(db.Integer, db.ForeignKey('materias.codigo'), nullable=False)
    nota = db.Column(db.Float, nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    estudiante = db.relationship('Estudiante', back_populates='notas')
    materia = db.relationship('Materia', back_populates='notas')
    
    def __init__(self, estudiante_id, materia_codigo, nota):
        self.estudiante_id = estudiante_id
        self.materia_codigo = materia_codigo
        self.nota = nota
    
    def __repr__(self):
        return f'<Nota Estudiante: {self.estudiante_id} - Materia: {self.materia_codigo} - Nota: {self.nota}>'

class Pago(db.Model):
    __tablename__ = 'pagos'
    
    recibo = db.Column(db.String(50), primary_key=True)
    estudiante_id = db.Column(db.String(20), db.ForeignKey('estudiantes.cedula'), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'deposito' o 'pago_materia'
    materia_codigo = db.Column(db.Integer, db.ForeignKey('materias.codigo'), nullable=True)  # Solo si es pago de materia

    estudiante = db.relationship('Estudiante', backref='pagos')
    materia = db.relationship('Materia', backref='pagos')

    def __init__(self, recibo, estudiante_id, monto, tipo, materia_codigo=None):
        self.recibo = recibo
        self.estudiante_id = estudiante_id
        self.monto = monto
        self.tipo = tipo
        self.materia_codigo = materia_codigo

    def __repr__(self):
        return f'<Pago Recibo: {self.recibo} - Estudiante: {self.estudiante_id} - Tipo: {self.tipo} - Monto: {self.monto}>'

