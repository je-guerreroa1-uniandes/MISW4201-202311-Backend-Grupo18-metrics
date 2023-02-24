import json
import hashlib
from faker.generator import random
from unittest import TestCase

from faker import Faker

from modelos import db, Usuario, Persona, Rol, Entrenador
from app import app


class TestPersona(TestCase):

    def setUp (self):
        self.data_factory = Faker()
        self.client = app.test_client()

        self.nombre_completo = self.data_factory.name()
        nombre_usuario = 'test_' + self.data_factory.name()
        contrasena = 'T1$' + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()

        # Se crea el usuario para identificarse en la aplicación
        usuario_nuevo = Usuario(usuario=nombre_usuario, contrasena=contrasena_encriptada, rol=Rol.ENTRENADOR)
        db.session.add(usuario_nuevo)
        nuevo_entrenador = Entrenador(
            nombre='Entrenador', apellido=nombre_usuario, usuario=usuario_nuevo)
        db.session.add(nuevo_entrenador)
        db.session.commit()

        self.entrenador_id = nuevo_entrenador.id

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

        self.personas_creadas = []

    def tearDown(self):
            for persona_creada in self.personas_creadas:
                persona = Persona.query.get(persona_creada.id)
                db.session.delete(persona)
                db.session.commit()


            usuario_login = Usuario.query.get(self.usuario_id)
            db.session.delete(usuario_login)
            usuario_entrenador = Entrenador.query.get(self.entrenador_id)
            db.session.delete(usuario_entrenador)
            usuario_persona = Usuario.query.get(self.usuario_persona_id)
            db.session.delete(usuario_persona)
            db.session.commit()

    def test_crear_persona(self):
        #Crear datos de persona
        nombre = 'test_' + self.data_factory.name().split()[0]
        apellido = 'test_' + self.data_factory.name().split()[1]
        talla = round(random.uniform(0.1, 0.99), 2)
        peso = round(random.uniform(0.1, 0.99), 2)
        edad = round(random.uniform(0.1, 0.99), 2)
        ingreso = self.data_factory.date()
        brazo = round(random.uniform(0.1, 0.99), 2)
        pecho = round(random.uniform(0.1, 0.99), 2)
        cintura = round(random.uniform(0.1, 0.99), 2)
        pierna = round(random.uniform(0.1, 0.99), 2)
        entrenando = True
        razon = ""
        terminado = "1900-01-01"

        #Datos de usuario al crear una persona
        nombre_usuario = 'test_' + self.data_factory.name()
        contrasena = 'T1$' + self.data_factory.word()

        # Crear el json con la persona a crear
        nueva_persona = {
            "nombre": nombre,
            "apellido": apellido,
            "talla": talla,
            "peso": peso,
            "edad": edad,
            "ingreso": ingreso,
            "brazo": brazo,
            "pecho": pecho,
            "cintura": cintura,
            "pierna": pierna,
            "entrenando": entrenando,
            "razon": razon,
            "terminado": terminado,
            "usuario": nombre + apellido,
            "contrasena": contrasena
        }

        # Definir endpoint, encabezados y hacer el llamado
        endpoint_persona = "/personas/" + str(self.usuario_id)
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        resultado_nueva_persona = self.client.post(endpoint_persona,
                                                     data=json.dumps(nueva_persona),
                                                     headers=headers)

        # Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta = json.loads(resultado_nueva_persona.get_data())
        persona = Persona.query.get(datos_respuesta['id'])
        self.personas_creadas.append(persona)
        self.usuario_persona_id = datos_respuesta['usuario_id']

        # Verificar que el llamado fue exitoso y que el objeto recibido tiene los datos iguales a los creados
        self.assertEqual(resultado_nueva_persona.status_code, 200)
        self.assertEqual(datos_respuesta['nombre'], persona.nombre)
        self.assertEqual(datos_respuesta['apellido'], persona.apellido)
        self.assertEqual(datos_respuesta['entrenador_id'], self.entrenador_id)
        self.assertIsNotNone(datos_respuesta['id'])