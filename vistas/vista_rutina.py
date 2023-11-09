from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from modelos.modelos import Ejercicio, db, Rutina, RutinaSchema

rutina_schema = RutinaSchema()

class VistaRutina(Resource):
    @jwt_required()
    def get(self, id_rutina):
        return rutina_schema.dump(Rutina.query.get_or_404(id_rutina))
    
    @jwt_required()
    def delete(self, id_rutina):
        rutina = Rutina.query.get_or_404(id_rutina)
        if len(rutina.entrenamientos) == 0:
            db.session.delete(rutina)
            db.session.commit()
            return '', 200
        else:
            return 'El ejercicio tiene entrenamientos asociados', 409


class VistaRutinas(Resource):
    @jwt_required()
    def put(self):
        edit_rutina = Rutina.query.get_or_404(request.json["id"])

        ejercicios_rq = request.json["ejercicios"]
        editEjercicios = [];  
        
        for ejercicio in ejercicios_rq:
            element =  Ejercicio.query.get_or_404(ejercicio['id'])
            editEjercicios.append(element)

        print(editEjercicios)

        edit_rutina.nombre = request.json["nombre"]
        edit_rutina.descripcion = request.json["descripcion"]
        edit_rutina.ejercicios = editEjercicios

        db.session.add(edit_rutina)
        db.session.commit()
        return rutina_schema.dump(edit_rutina)

    @jwt_required()
    def post(self):
        nueva_rutina = Rutina( \
            nombre=request.json["nombre"], \
            descripcion=request.json["descripcion"], \
        )

        ejercicios = request.json["ejercicios"] 

        for ejercicio in ejercicios:
            element =  Ejercicio.query.get_or_404(ejercicio['id'])
            nueva_rutina.ejercicios.append(element)


        db.session.add(nueva_rutina)
        db.session.commit()
        return rutina_schema.dump(nueva_rutina)

    @jwt_required()
    def get(self):
        rutinas = Rutina.query.all()
        return [rutina_schema.dump(rutina) for rutina in rutinas]