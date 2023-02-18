import json
import hashlib
from unittest import TestCase

from faker import Faker

from modelos import db, Usuario, Entrenador
from app import app


class TestEntrenadores(TestCase):

    def setUp (self):
        self.data_factory = Faker()
        self.client = app.test_client()

        self.nombre_completo = self.data_factory.name()
        nombre_usuario = 'test_' + self.data_factory.name()
        contrasena = 'T1$' + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()

        # Se crea el usuario para identificarse en la aplicación
        usuario_nuevo = Usuario(usuario=nombre_usuario, contrasena=contrasena_encriptada)
        db.session.add(usuario_nuevo)
        db.session.commit()

        usuario_login = {
            "usuario": nombre_usuario,
            "contrasena": contrasena
        }

        solicitud_login = self.client.post("/login",
                                           data=json.dumps(usuario_login),
                                           headers={'Content-Type': 'application/json'})

        respuesta_login = json.loads(solicitud_login.get_data())

        self.token = respuesta_login["token"]
        self.usuario_id = respuesta_login["id"]

        self.entrenadores_creados = []

    def tearDown(self):
            for entrenador_creado in self.entrenadores_creados:
                entrenador = Entrenador.query.get(entrenador_creado.id)
                db.session.delete(entrenador)
                db.session.commit()

    def test_listar_entrenadores(self):
        # Generar 10 ejercicios con datos aleatorios
        for i in range(0, 10):
            # Crear los datos del ejercicio
            nombre_entrenador = 'test_' + self.data_factory.name().split()[0]
            apellido_entrenador = 'test_' + self.data_factory.name().split()[1]

            # Crear el ejercicio con los datos originales para obtener su id
            entrenador = Entrenador(
                    nombre=nombre_entrenador,
                    apellido=apellido_entrenador
                    )
            db.session.add(entrenador)
            db.session.commit()
            self.entrenadores_creados.append(entrenador)