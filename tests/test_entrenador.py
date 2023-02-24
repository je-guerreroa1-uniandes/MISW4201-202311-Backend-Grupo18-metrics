import json
import hashlib
from unittest import TestCase
from unittest import skip

from faker import Faker

from modelos import db, Usuario, Entrenador, Rol
from app import app


class TestEntrenador(TestCase):

    def setUp (self):
        self.data_factory = Faker()
        self.client = app.test_client()

        self.nombre_completo = self.data_factory.name()
        nombre_usuario = 'test_' + self.data_factory.name()
        contrasena = 'T1$' + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()

        # Se crea el usuario para identificarse en la aplicación
        usuario_nuevo = Usuario(usuario=nombre_usuario, contrasena=contrasena_encriptada, rol=Rol.ADMINISTRADOR)
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

            usuario_login = Usuario.query.get(self.usuario_id)
            db.session.delete(usuario_login)
            db.session.commit()

    @skip('HU029')
    def test_crear_entrenador(self):
        #Crear datos de entrenador
        nombre_entrenador = 'test_' + self.nombre_completo.split()[0]
        apellido_entrenador = 'test_' + self.nombre_completo.split()[1]

        # Crear el json con el ejercicio a crear
        nuevo_entrenador = {
            "nombre": nombre_entrenador,
            "apellido": apellido_entrenador,
            "usuario_id": self.usuario_id
        }

        # Definir endpoint, encabezados y hacer el llamado
        endpoint_entrenadores = "/entrenador"
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        resultado_nuevo_entrenador = self.client.post(endpoint_entrenadores,
                                                     data=json.dumps(nuevo_entrenador),
                                                     headers=headers)

        # Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta = json.loads(resultado_nuevo_entrenador.get_data())
        entrenador = Entrenador.query.get(datos_respuesta['id'])
        self.entrenadores_creados.append(entrenador)

        # Verificar que el llamado fue exitoso y que el objeto recibido tiene los datos iguales a los creados
        self.assertEqual(resultado_nuevo_entrenador.status_code, 200)
        self.assertEqual(datos_respuesta['nombre'], entrenador.nombre)
        self.assertEqual(datos_respuesta['apellido'], entrenador.apellido)
        self.assertEqual(datos_respuesta['usuario'], str(self.usuario_id))
        self.assertIsNotNone(datos_respuesta['id'])
