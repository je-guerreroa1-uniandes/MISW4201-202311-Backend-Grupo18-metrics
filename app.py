from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api

from modelos import db
from vistas import \
    VistaSignIn, VistaLogIn, \
    VistaPersona, VistaPersonas, \
    VistaEjercicio, VistaEjercicios, \
    VistaReporte, VistaPersonaUsuario
from vistas.vista_entrenador import VistaEntrenador
from vistas.vista_entrenadores import VistaEntrenadores
from vistas.vista_entrenamientos import VistaEntrenamientoConRutina, VistaEntrenamientos, VistaEntrenamiento, VistaRutinaEntrenamiento, VistaRutinaEntrenamientos
from vistas.vista_rutina import VistaRutina, VistaRutinas

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbapp.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config['PROPAGATE_EXCEPTIONS'] = True

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

cors = CORS(app)

api = Api(app)
api.add_resource(VistaSignIn, '/signin')
api.add_resource(VistaLogIn, '/login')
api.add_resource(VistaEntrenadores, '/entrenadores')
api.add_resource(VistaEntrenador, '/entrenador')
api.add_resource(VistaPersonas, '/personas/<int:id_usuario>')
api.add_resource(VistaPersonaUsuario, '/persona/usuario/<int:id_usuario>')
api.add_resource(VistaPersona, '/persona/<int:id_persona>')
api.add_resource(VistaEjercicios, '/ejercicios')
api.add_resource(VistaEjercicio, '/ejercicio/<int:id_ejercicio>')

#Entrenamiento con ejercicio
api.add_resource(VistaEntrenamientos, '/entrenamientos/<int:id_persona>')
api.add_resource(VistaEntrenamiento, '/entrenamiento/<int:id_entrenamiento>')

#Entrenamiento con rutina
api.add_resource(VistaRutinaEntrenamientos, '/rutinas/entrenar')
api.add_resource(VistaRutinaEntrenamiento, '/rutinas/entrenar/<int:id_entrenamiento>')
api.add_resource(VistaEntrenamientoConRutina, '/entrenamientos/rutina/<int:id>')

api.add_resource(VistaReporte, '/persona/<int:id_persona>/reporte')

api.add_resource(VistaRutina, '/rutina/<int:id_rutina>')
api.add_resource(VistaRutinas, '/rutinas')

jwt = JWTManager(app)
