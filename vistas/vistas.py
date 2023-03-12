from flask import request, abort
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from .utilidad_reporte import UtilidadReporte
import hashlib

from modelos import \
    db, \
    Ejercicio, EjercicioSchema, \
    Persona, PersonaSchema, \
    Entrenamiento, EntrenamientoSchema, \
    Usuario, UsuarioSchema, \
    ReporteGeneralSchema, ReporteDetalladoSchema, \
    Entrenador, Rol


ejercicio_schema = EjercicioSchema()
persona_schema = PersonaSchema()
entrenamiento_schema = EntrenamientoSchema()
usuario_schema = UsuarioSchema()
reporte_general_schema = ReporteGeneralSchema()
reporte_detallado_schema = ReporteDetalladoSchema()


class VistaSignIn(Resource):

    def post(self):
        usuario = Usuario.query.filter(
            Usuario.usuario == request.json["usuario"]).first()
        if usuario is None:
            contrasena_encriptada = hashlib.md5(
                request.json["contrasena"].encode('utf-8')).hexdigest()
            nuevo_usuario = Usuario(
                usuario=request.json["usuario"], contrasena=contrasena_encriptada, rol=Rol.ENTRENADOR)
            nuevo_entrenador = Entrenador(
                nombre='Entrenador', apellido=request.json["usuario"], usuario=nuevo_usuario)
            db.session.add(nuevo_entrenador)
            db.session.commit()
            # token_de_acceso = create_access_token(identity=nuevo_usuario.id)
            return {"mensaje": "usuario creado exitosamente", "id": nuevo_usuario.id}
        else:
            return "El usuario ya existe", 404

    def put(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        usuario.contrasena = request.json.get("contrasena", usuario.contrasena)
        db.session.commit()
        return usuario_schema.dump(usuario)

    def delete(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return '', 204


class VistaLogIn(Resource):

    def post(self):
        contrasena_encriptada = hashlib.md5(
            request.json["contrasena"].encode('utf-8')).hexdigest()
        usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"],
                                       Usuario.contrasena == contrasena_encriptada).first()
        db.session.commit()
        if usuario is None:
            return "El usuario no existe", 404
        else:
            token_de_acceso = create_access_token(identity=usuario.id)
            return {"mensaje": "Inicio de sesión exitoso", "token": token_de_acceso, "id": usuario.id, "rol": usuario.rol.name}


class VistaPersonas(Resource):
    @jwt_required()
    def get(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        personas = []

        if usuario.rol == Rol.ADMINISTRADOR:
            personas = Persona.query.all()
        elif usuario.rol == Rol.ENTRENADOR:
            entrenador = Entrenador.query.filter_by(
                usuario_id=id_usuario).first_or_404()
            personas = entrenador.personas
        else:
            abort(500, description='Rol de usuario no definido')

        return [persona_schema.dump(persona) for persona in personas]

    @jwt_required()
    def post(self, id_usuario):
        usuario = Usuario.query.filter(
            Usuario.usuario == request.json["usuario"]).first()
        if usuario is not None:
            abort(500, description="usuario ya existe")

        entrenador = Entrenador.query.filter_by(
            usuario_id=id_usuario).first_or_404()
        contrasena_encriptada = hashlib.md5(
            request.json["contrasena"].encode('utf-8')).hexdigest()
        nuevo_usuario = Usuario(
            usuario=request.json["usuario"], contrasena=contrasena_encriptada, rol=Rol.PERSONA)
        db.session.add(nuevo_usuario)
        db.session.commit()
        nueva_persona = Persona(
            nombre=request.json["nombre"],
            apellido=request.json["apellido"],
            talla=float(request.json["talla"]),
            peso=float(request.json["peso"]),
            edad=float(request.json["edad"]),
            ingreso=datetime.strptime(request.json["ingreso"], '%Y-%m-%d'),
            brazo=float(request.json["brazo"]),
            pecho=float(request.json["pecho"]),
            cintura=float(request.json["cintura"]),
            pierna=float(request.json["pierna"]),
            entrenando=bool(request.json["entrenando"]),
            razon=request.json["razon"],
            terminado=datetime.strptime(request.json["terminado"], '%Y-%m-%d'),
            entrenador_id=entrenador.id,
            usuario_id=nuevo_usuario.id
        )
        entrenador.personas.append(nueva_persona)
        db.session.commit()
        return persona_schema.dump(nueva_persona)


class VistaPersona(Resource):
    @jwt_required()
    def get(self, id_persona):
        persona = Persona.query.get_or_404(id_persona)
        return persona_schema.dump(persona)

    @jwt_required()
    def put(self, id_persona):
        persona = Persona.query.get_or_404(id_persona)
        persona.nombre = request.json["nombre"]
        persona.apellido = request.json["apellido"]
        persona.talla = float(request.json["talla"])
        persona.peso = float(request.json["peso"])
        persona.edad = float(request.json["edad"])
        persona.ingreso = datetime.strptime(
            request.json["ingreso"], '%Y-%m-%d')
        persona.brazo = float(request.json["brazo"])
        persona.pecho = float(request.json["pecho"])
        persona.cintura = float(request.json["cintura"])
        persona.pierna = float(request.json["pierna"])
        persona.entrenando = bool(request.json["entrenando"])
        persona.razon = request.json["razon"]
        persona.terminado = datetime.strptime(
            request.json["terminado"], '%Y-%m-%d')
        persona.usuario.usuario = request.json["usuario"]
        if request.json["contrasena"]:
            contrasena_encriptada = hashlib.md5(
                request.json["contrasena"].encode('utf-8')).hexdigest()
            persona.usuario.contrasena = contrasena_encriptada
        db.session.commit()
        return persona_schema.dump(persona)

    @jwt_required()
    def delete(self, id_persona):
        persona = Persona.query.get_or_404(id_persona)
        if not persona.entrenamientos:
            db.session.delete(persona)
            db.session.commit()
            return '', 204
        else:
            return 'La persona tiene entrenamientos asociados', 409


class VistaPersonaUsuario(Resource):
    @jwt_required()
    def get(self, id_usuario):
        persona = Persona.query.filter_by(usuario_id=id_usuario).first_or_404()
        return persona_schema.dump(persona)


class VistaEjercicios(Resource):
    @jwt_required()
    def get(self):
        ejercicios = Ejercicio.query.all()
        return [ejercicio_schema.dump(ejercicio) for ejercicio in ejercicios]

    @jwt_required()
    def post(self):
        nuevo_ejercicio = Ejercicio(
            nombre=request.json["nombre"],
            descripcion=request.json["descripcion"],
            video=request.json["video"],
            calorias=float(request.json["calorias"]),
        )
        db.session.add(nuevo_ejercicio)
        db.session.commit()
        return ejercicio_schema.dump(nuevo_ejercicio)


class VistaEjercicio(Resource):
    @jwt_required()
    def get(self, id_ejercicio):
        return ejercicio_schema.dump(Ejercicio.query.get_or_404(id_ejercicio))

    @jwt_required()
    def put(self, id_ejercicio):
        ejercicio = Ejercicio.query.get_or_404(id_ejercicio)
        ejercicio.nombre = request.json["nombre"]
        ejercicio.descripcion = request.json["descripcion"]
        ejercicio.video = request.json["video"]
        ejercicio.calorias = float(request.json["calorias"])
        db.session.commit()
        return ejercicio_schema.dump(ejercicio)

    @jwt_required()
    def delete(self, id_ejercicio):
        ejercicio = Ejercicio.query.get_or_404(id_ejercicio)
        if not ejercicio.entrenamientos:
            db.session.delete(ejercicio)
            db.session.commit()
            return '', 204
        else:
            return 'El ejercicio tiene entrenamientos asociados', 409


class VistaReporte(Resource):

    @jwt_required()
    def get(self, id_persona):
        reporte = []
        reporte_entrenamiento = []
        utilidad = UtilidadReporte()
        data_persona = Persona.query.get_or_404(id_persona)
        imc_calculado = utilidad.calcular_imc(
            data_persona.talla, data_persona.peso)
        clasificacion_imc_calculado = utilidad.dar_clasificacion_imc(
            imc_calculado)

        # Report header
        reporte_persona = dict(persona=data_persona, imc=imc_calculado,
                               clasificacion_imc=clasificacion_imc_calculado)
        reporte_persona_schema = reporte_general_schema.dump(reporte_persona)

        # Código no usado
        for entrenamiento in data_persona.entrenamientos:
            data_entrenamiento = dict(
                fecha=entrenamiento.fecha, repeticiones=entrenamiento.repeticiones, calorias=1)
            reporte_entrenamiento.append(
                reporte_detallado_schema.dump(data_entrenamiento))

        # Resultados entrenamientos
        reporte_persona_schema['resultados'] = utilidad.dar_resultados(
            data_persona.entrenamientos,
            data_persona.entrenamientos_rutina
        )

        return reporte_persona_schema
