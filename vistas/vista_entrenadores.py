from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource

from modelos import db, EntrenadorSchema, Entrenador

entrenador_schema = EntrenadorSchema

class VistaEntrenadores(Resource):
    @jwt_required()
    def get(self):
        entrenadores = Entrenador.query.all()
        return [entrenador_schema.dump(entrenador) for entrenador in entrenadores]

    @jwt_required()
    def post(self):
        nuevo_ejercicio = Ejercicio( \
            nombre=request.json["nombre"], \
            descripcion=request.json["descripcion"], \
            video=request.json["video"], \
            calorias=float(request.json["calorias"]),
        )
        db.session.add(nuevo_ejercicio)
        db.session.commit()
        return entrenador_schema.dump(nuevo_ejercicio)