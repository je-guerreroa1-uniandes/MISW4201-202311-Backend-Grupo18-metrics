from flask import request, abort
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
import hashlib

from modelos import db, EntrenadorSchema, Entrenador, Usuario, Rol

entrenador_schema = EntrenadorSchema()

class VistaEntrenador(Resource):
    @jwt_required()
    def get(self, id_entrenador):
        entrenador = Entrenador.query.get_or_404(id_entrenador)
        return [entrenador_schema.dump(entrenador) for usuario in entrenador.usuario]

    @jwt_required()
    def post(self):
        usuario = Usuario.query.filter(
            Usuario.usuario == request.json["usuario"]).first()
        if usuario is not None:
            abort(500, description="usuario ya existe")
        if usuario is not None:
            abort(500, description="Usuario ya existe")

        contrasena_encriptada = hashlib.md5(
            request.json["contrasena"].encode('utf-8')).hexdigest()
        nuevo_usuario = Usuario(
            usuario=request.json["usuario"], contrasena=contrasena_encriptada, rol=Rol.ENTRENADOR)
        db.session.add(nuevo_usuario)
        db.session.commit()

        nuevo_entrenador = Entrenador( \
            nombre=request.json["nombre"], \
            apellido=request.json["apellido"], \
            usuario_id=nuevo_usuario.id \
            )
        # usuario.entrenadores.append(nuevo_entrenador)
        # db.session.add(usuario)
        db.session.add(nuevo_entrenador)
        db.session.commit()
        return entrenador_schema.dump(nuevo_entrenador)