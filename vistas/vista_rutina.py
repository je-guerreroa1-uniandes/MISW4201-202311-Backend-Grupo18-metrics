from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from modelos.modelos import Ejercicio, db, Rutina, RutinaSchema

rutina_schema = RutinaSchema()

class VistaRutina(Resource):
    @jwt_required()
    def get(self, id_rutina):
        return rutina_schema.dump(Rutina.query.get_or_404(id_rutina))


class VistaRutinas(Resource):
    @jwt_required()
    def post(self):
        nuevaRutina = Rutina( \
            nombre=request.json["nombre"], \
            descripcion=request.json["descripcion"], \
        )

        ejercicios = request.json["ejercicios"] 

        for ejercicio in ejercicios:
            element =  Ejercicio.query.get_or_404(ejercicio['id'])
            nuevaRutina.ejercicios.append(element)


        db.session.add(nuevaRutina)
        db.session.commit()
        return rutina_schema.dump(nuevaRutina)

    @jwt_required()
    def get(self):
        rutinas = Rutina.query.all()
        return [rutina_schema.dump(rutina) for rutina in rutinas]