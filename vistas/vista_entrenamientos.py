from datetime import datetime
from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from modelos import db
from modelos.modelos import Ejercicio, EjercicioSchema, Entrenamiento, EntrenamientoRutina, EntrenamientoRutinaSchema, EntrenamientoSchema, Persona, Rutina, RutinaSchema

entrenamiento_schema = EntrenamientoSchema()
entrenamiento_rutina_schema = EntrenamientoRutinaSchema()
ejercicio_schema = EjercicioSchema()
rutina_schema = RutinaSchema()

class VistaEntrenamientos(Resource):
    @jwt_required()
    def get(self, id_persona):
        persona = Persona.query.get_or_404(id_persona)
        entrenamiento_array = []

        for entrenamiento in persona.entrenamientos:
            ejercicio = Ejercicio.query.get_or_404(entrenamiento.ejercicio)
            entrenamiento_schema_dump = entrenamiento_schema.dump(
                entrenamiento)
            entrenamiento_schema_dump['ejercicio'] = ejercicio_schema.dump(
                ejercicio)
            entrenamiento_array.append(entrenamiento_schema_dump)
        return [entrenamiento for entrenamiento in entrenamiento_array]

    @jwt_required()
    def post(self, id_persona):
        type =  request.json["type"]
            
        if type == '1' :
            print(datetime.strptime(request.json["fecha"], '%Y-%m-%d'))
            nuevo_entrenamiento = Entrenamiento(
                tiempo=datetime.strptime(request.json["tiempo"], '%H:%M:%S').time(),
                repeticiones=float(request.json["repeticiones"]),
                fecha=datetime.strptime(request.json["fecha"], '%Y-%m-%d').date(),
                ejercicio=int(request.json["ejercicio"]),
                persona=id_persona
            )

            db.session.add(nuevo_entrenamiento)
            db.session.commit()
            return entrenamiento_schema.dump(nuevo_entrenamiento)
        else :
            print("se fue por rutinas")
            nuevo_entrenamiento = EntrenamientoRutina(
                tiempo=datetime.strptime(request.json["tiempo"], '%H:%M:%S').time(),
                repeticiones=float(request.json["repeticiones"]),
                fecha=datetime.strptime(request.json["fecha"], '%Y-%m-%d').date(),
                rutina=int(request.json["ejercicio"]),
                persona=id_persona
            )

            db.session.add(nuevo_entrenamiento)
            db.session.commit()
            return entrenamiento_rutina_schema.dump(nuevo_entrenamiento)

class VistaEntrenamiento(Resource):
    @jwt_required()
    def get(self, id_entrenamiento):
        return entrenamiento_schema.dump(Entrenamiento.query.get_or_404(id_entrenamiento))

    @jwt_required()
    def put(self, id_entrenamiento):  
        entrenamiento = Entrenamiento.query.get_or_404(id_entrenamiento) 
        entrenamiento.tiempo = datetime.strptime(request.json["tiempo"], '%H:%M:%S').time()
        entrenamiento.repeticiones=float(request.json["repeticiones"])
        entrenamiento.fecha=datetime.strptime(request.json["fecha"], '%Y-%m-%d').date()

        persona = Persona.query.get_or_404(request.json['persona'])
        ejercicio = Ejercicio.query.get_or_404(request.json['ejercicio'])
        entrenamiento.ejercicio=ejercicio.id
        entrenamiento.persona=persona.id

        db.session.add(entrenamiento)
        db.session.commit()
        return entrenamiento_schema.dump(entrenamiento)

    @jwt_required()
    def delete(self, id_entrenamiento):
        print('eliminar entrenamiento ejercicios')
        entrenamiento = Entrenamiento.query.get_or_404(id_entrenamiento)
        db.session.delete(entrenamiento)
        db.session.commit()
        return '', 200
    
class VistaEntrenamientoConRutina(Resource):
    @jwt_required()
    def delete(self, id):
        print('eliminar entrenamiento rutinas')
        entrenamiento = EntrenamientoRutina.query.get_or_404(id)
        db.session.delete(entrenamiento)
        db.session.commit()
        return '', 200
    
    @jwt_required()
    def put(self, id):  
        entrenamiento = Entrenamiento.query.get_or_404(id) 
        entrenamiento.tiempo = datetime.strptime(request.json["tiempo"], '%H:%M:%S').time()
        entrenamiento.repeticiones=float(request.json["repeticiones"])
        entrenamiento.fecha=datetime.strptime(request.json["fecha"], '%Y-%m-%d').date()

        persona = Persona.query.get_or_404(request.json['persona'])
        ejercicio = Rutina.query.get_or_404(request.json['ejercicio'])
        entrenamiento.ejercicio=ejercicio.id
        entrenamiento.persona=persona.id

        db.session.add(entrenamiento)
        db.session.commit()
        return entrenamiento_schema.dump(entrenamiento)

    @jwt_required()
    def get(self, id):
        persona = Persona.query.get_or_404(id)
        entrenamiento_array = []

        for entrenamiento in persona.entrenamientos_rutina:
            entrenamiento_rutina = Rutina.query.get_or_404(entrenamiento.rutina)
            entrenamiento_rutina_schema_dump = entrenamiento_schema.dump(entrenamiento)
            entrenamiento_rutina_schema_dump['rutina'] = rutina_schema.dump(entrenamiento_rutina)
            entrenamiento_array.append(entrenamiento_rutina_schema_dump)

        return [entrenamiento for entrenamiento in entrenamiento_array]

class VistaRutinaEntrenamiento(Resource):
    @jwt_required()
    def get(self):
        rutinas = Rutina.query.all()
        response_array = []

        for rutina in rutinas:
            if len(rutina.ejercicios)>=3 and len(rutina.ejercicios)<=5:
                response_array.append(rutina);

        return [rutina_schema.dump(rutina) for rutina in response_array]
