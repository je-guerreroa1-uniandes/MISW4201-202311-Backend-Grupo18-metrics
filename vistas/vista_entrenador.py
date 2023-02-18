from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource

from modelos import db, EntrenadorSchema, Entrenador, Usuario

entrenador_schema = EntrenadorSchema()

class VistaEntrenador(Resource):
    @jwt_required()
    def get(self, id_entrenador):
        entrenador = Entrenador.query.get_or_404(id_entrenador)
        return [entrenador_schema.dump(entrenador) for usuario in entrenador.usuario]

    @jwt_required()
    def post(self):
        usuario = Usuario.query.get_or_404(request.json["usuario_id"])
        nuevo_entrenador = Entrenador( \
            nombre=request.json["nombre"], \
            apellido=request.json["apellido"], \
            usuario=usuario \
            )
        usuario.entrenadores.append(nuevo_entrenador)
        db.session.add(usuario)
        db.session.add(nuevo_entrenador)
        db.session.commit()
        return entrenador_schema.dump(nuevo_entrenador)