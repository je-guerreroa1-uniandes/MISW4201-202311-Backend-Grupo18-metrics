import json
import hashlib
from unittest import TestCase

from faker import Faker
from passlib.hash import bcrypt

from modelos import db, Usuario, Entrenador, Rol
from app import app


class TestEntrenador(TestCase):

    def setUp (self):
        self.data_factory = Faker()
        self.client = app.test_client()
        self.content_type = 'application/json'
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
                                           headers={'Content-Type': self.content_type})

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

    def test_crear_entrenador(self):
        # Crear datos de entrenador
        # Datos entrenador
        nombre_entrenador = 'test_' + self.data_factory.name().split()[0]
        apellido_entrenador = 'test_' + self.data_factory.name().split()[1]
        # Datos de usuario
        usuario = nombre_entrenador + apellido_entrenador
        contrasena = 'T1$' + self.data_factory.word()

        # Crear el json con el ejercicio a crear
        nuevo_entrenador = {
            "nombre": nombre_entrenador,
            "apellido": apellido_entrenador,
            "usuario": usuario,
            "contrasena": contrasena
        }

        # Definir endpoint, encabezados y hacer el llamado
        endpoint_entrenadores = "/entrenador"
        headers = {'Content-Type': self.content_type, "Authorization": "Bearer {}".format(self.token)}

        resultado_nuevo_entrenador = self.client.post(endpoint_entrenadores,
                                                     data=json.dumps(nuevo_entrenador),
                                                     headers=headers)

        # Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta = json.loads(resultado_nuevo_entrenador.get_data())
        entrenador = Entrenador.query.get(datos_respuesta['id'])
        self.entrenadores_creados.append(entrenador)

        nuevo_usuario = Usuario.query.filter(
            Usuario.usuario == usuario).first()

        # Verificar que el llamado fue exitoso y que el objeto recibido tiene los datos iguales a los creados
        self.assertEqual(resultado_nuevo_entrenador.status_code, 200)
        self.assertEqual(datos_respuesta['nombre'], entrenador.nombre)
        self.assertEqual(datos_respuesta['apellido'], entrenador.apellido)
        self.assertEqual(datos_respuesta['usuario'], nuevo_usuario.id)
        self.assertIsNotNone(datos_respuesta['id'])


def test_actualizar_entrenador(self):
    # First, create an entrenador that we will update
    entrenador = self.create_entrenador_helper()

    # Now, define the update data
    updated_data = {
        "nombre": 'Updated_' + entrenador.nombre,
        "apellido": 'Updated_' + entrenador.apellido,
        # Add any other fields you want to update
    }

    # Define the endpoint and headers for the update
    endpoint = f"/entrenador/{entrenador.id}"
    headers = {
        'Content-Type': self.content_type,
        "Authorization": f"Bearer {self.token}"
    }

    # Send the PUT request to update the entrenador
    response = self.client.put(endpoint, data=json.dumps(updated_data), headers=headers)

    # Check that the update was successful
    self.assertEqual(response.status_code, 200)

    # Fetch the updated entrenador from the database
    updated_entrenador = Entrenador.query.get(entrenador.id)

    # Verify the entrenador's fields were updated
    self.assertEqual(updated_entrenador.nombre, updated_data['nombre'])
    self.assertEqual(updated_entrenador.apellido, updated_data['apellido'])

    # Optionally check if 'updated_at' field has been changed
    # This assumes your model has an 'updated_at' field that is set to the current time on update
    # self.assertNotEqual(updated_entrenador.updated_at, entrenador.updated_at)

    # Clean up by deleting the updated entrenador
    self.entrenadores_creados.append(updated_entrenador)


# Helper method to create an entrenador
def create_entrenador_helper(self):
    nombre_entrenador = 'test_' + self.data_factory.name().split()[0]
    apellido_entrenador = 'test_' + self.data_factory.name().split()[1]
    usuario = nombre_entrenador + apellido_entrenador
    contrasena = 'T1$' + self.data_factory.word()
    contrasena_encriptada = bcrypt.hash(contrasena)

    # Create the user associated with the entrenador
    usuario_nuevo = Usuario(usuario=usuario, contrasena=contrasena_encriptada, rol=Rol.ADMINISTRADOR)
    db.session.add(usuario_nuevo)
    db.session.commit()

    # Now create the entrenador
    nuevo_entrenador = Entrenador(nombre=nombre_entrenador, apellido=apellido_entrenador, usuario_id=usuario_nuevo.id)
    db.session.add(nuevo_entrenador)
    db.session.commit()

    return nuevo_entrenador