from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from enum import Enum

db = SQLAlchemy()


class Ejercicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    descripcion = db.Column(db.String(512))
    video = db.Column(db.String(512))
    calorias = db.Column(db.Float)
    entrenamientos = db.relationship('Entrenamiento')


class Persona(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    apellido = db.Column(db.String(128))
    talla = db.Column(db.Float)
    peso = db.Column(db.Float)
    edad = db.Column(db.Float)
    ingreso = db.Column(db.Date)
    brazo = db.Column(db.Float)
    pecho = db.Column(db.Float)
    cintura = db.Column(db.Float)
    pierna = db.Column(db.Float)
    entrenando = db.Column(db.Boolean, default=True)
    razon = db.Column(db.String(512))
    terminado = db.Column(db.Date)
    entrenamientos = db.relationship(
        'Entrenamiento', cascade='all, delete, delete-orphan')
    usuario_id = db.Column(
        db.Integer, db.ForeignKey('usuario.id'), unique=True)
    entrenador_id = db.Column(db.Integer, db.ForeignKey('entrenador.id'))


class Entrenador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    apellido = db.Column(db.String(128))
    personas = db.relationship('Persona')
    usuario_id = db.Column(
        db.Integer, db.ForeignKey('usuario.id'), unique=True)
    usuario = db.relationship('Usuario')


class Rol(Enum):
    ADMINISTRADOR = 1
    ENTRENADOR = 2
    PERSONA = 3


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50))
    contrasena = db.Column(db.String(50))
    rol = db.Column(db.Enum(Rol))


class Entrenamiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tiempo = db.Column(db.Time)
    repeticiones = db.Column(db.Integer)
    fecha = db.Column(db.Date)
    ejercicio = db.Column(db.Integer, db.ForeignKey('ejercicio.id'))
    persona = db.Column(db.Integer, db.ForeignKey('persona.id'))


class EjercicioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Ejercicio
        include_relationships = True
        include_fk = True
        load_instance = True

    id = fields.String()
    calorias = fields.String()


class PersonaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Persona
        include_relationships = True
        include_fk = True
        load_instance = True

    entrenamientos = fields.List(fields.Nested(lambda: EntrenamientoSchema()))


class EntrenadorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Entrenador
        include_relationships = True
        include_fk = True
        load_instance = True

    personas = fields.List(fields.Nested(
        PersonaSchema, exclude=('entrenamientos',)))


class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True


class ReporteGeneralSchema(Schema):
    persona = fields.Nested(PersonaSchema())
    imc = fields.Float()
    clasificacion_imc = fields.String()


class ReporteDetalladoSchema(Schema):
    fecha = fields.String()
    repeticiones = fields.Float()
    calorias = fields.Float()


class EntrenamientoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Entrenamiento
        include_relationships = True
        include_fk = True
        load_instance = True
