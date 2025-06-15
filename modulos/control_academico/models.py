from modulos import db

class Materia(db.Model):
    __tablename__ ='materias'

    codigo = db.Column(db.String(20), primary_key=True, unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    profesor = db.Column(db.String(20), db.ForeignKey('profesores.cedula'), nullable=True)

    # Relaciones
    inscripciones = db.relationship('Inscripcion', back_populates='materia')
    cortes = db.relationship('Corte', back_populates='materia')

    def __init__(self, codigo, nombre, profesor=None):
        self.codigo = codigo
        self.nombre = nombre
        self.profesor = profesor

    def __repr__(self):
        return f'<Materia {self.codigo}>'

class Corte(db.Model):
    __tablename__ = 'cortes'

    id = db.Column(db.String(20), primary_key=True, unique=True)
    materia_codigo = db.Column(db.String(20), db.ForeignKey('materias.codigo'), nullable=False)
    seccion = db.Column(db.String(20), nullable=False)
    periodo = db.Column(db.String(20), nullable=False)

    # relaciones
    materia = db.relationship('Materia', back_populates='cortes')
    inscripciones = db.relationship('Inscripcion', back_populates='corte')

    def __init__(self, id, materia_codigo, seccion, periodo):
        self.id = id
        self.materia_codigo = materia_codigo
        self.seccion = seccion
        self.periodo = periodo

    def __repr__(self):
        return f'<Corte {self.id} - {self.materia_codigo} - {self.seccion} - {self.periodo}>'

class Inscripcion(db.Model):
    __tablename__ = 'inscripciones'

    id = db.Column(db.Integer, primary_key=True)
    estudiante_cedula = db.Column(db.String(20), db.ForeignKey('estudiantes.cedula'), nullable=False)
    materia_codigo = db.Column(db.String(20), db.ForeignKey('materias.codigo'), nullable=False)
    corte_id = db.Column(db.String(20), db.ForeignKey('cortes.id'), nullable=False)
    nota = db.Column(db.Float, nullable=True)
    fecha_inscripcion = db.Column(db.DateTime, nullable=False)
    estado_pago = db.Column(db.Boolean, default=False)

    # Relaciones
    estudiante = db.relationship('Estudiante', back_populates='inscripciones')
    materia = db.relationship('Materia', back_populates='inscripciones')
    corte = db.relationship('Corte', back_populates='inscripciones')

    def __init__(self, estudiante_cedula, materia_codigo, corte_id, nota, fecha_inscripcion, estado_pago=False):
        self.estudiante_cedula = estudiante_cedula
        self.materia_codigo = materia_codigo
        self.corte_id = corte_id
        self.nota = nota
        self.fecha_inscripcion = fecha_inscripcion
        self.estado_pago = estado_pago

    def __repr__(self):
        return f'<Inscripcion {self.id} - Estudiante: {self.estudiante_cedula} - Materia: {self.materia_codigo} - Corte: {self.corte_id}>' 