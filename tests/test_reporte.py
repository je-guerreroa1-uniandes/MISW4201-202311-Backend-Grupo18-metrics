import json
import hashlib
from datetime import datetime

from faker.generator import random
from unittest import TestCase

from faker import Faker

from modelos import db, Usuario, Persona, Rol, Entrenador, Entrenamiento, Ejercicio, Rutina, EntrenamientoRutina
from app import app
from vistas import UtilidadReporte

class TestReporte(TestCase):

    def setUp(self):
        self.personas_creadas = []
        self.entrenadores_creados = []
        self.usuarios_creados = []
        self.data_factory = Faker()
        self.client = app.test_client()
        self.content_type = 'application/json'

        self.nombre_completo = self.data_factory.name()
        nombre_usuario = 'test_' + self.data_factory.name()
        contrasena = 'T1$' + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()

        # Se crea el usuario para identificarse en la aplicación
        usuario_nuevo = Usuario(usuario=nombre_usuario, contrasena=contrasena_encriptada, rol=Rol.ENTRENADOR)
        db.session.add(usuario_nuevo)
        db.session.commit()
        nuevo_entrenador = Entrenador(
            nombre='Entrenador', apellido=nombre_usuario, usuario=usuario_nuevo)
        db.session.add(nuevo_entrenador)
        db.session.commit()

        self.entrenador_id = nuevo_entrenador.id

        usuario_login = {
            "usuario": nombre_usuario,
            "contrasena": contrasena
        }

        # Login como usuario para pruebas
        solicitud_login = self.client.post("/login",
                                           data=json.dumps(usuario_login),
                                           headers={'Content-Type': self.content_type})

        respuesta_login = json.loads(solicitud_login.get_data())

        self.token = respuesta_login["token"]
        self.usuario_id = respuesta_login["id"]

        # Crear datos de persona
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

        # Datos de usuario al crear una persona
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
        headers = {'Content-Type': self.content_type, "Authorization": "Bearer {}".format(self.token)}

        resultado_nueva_persona = self.client.post(endpoint_persona,
                                                   data=json.dumps(nueva_persona),
                                                   headers=headers)

        # Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta = json.loads(resultado_nueva_persona.get_data())
        self.persona = Persona.query.get(datos_respuesta['id'])
        self.personas_creadas.append(self.persona)
        self.usuario_persona_id = datos_respuesta['usuario_id']
        usuario_persona = Usuario.query.get(self.usuario_persona_id)
        self.usuarios_creados.append(usuario_persona)

        # Create and commit a new Ejercicio instance to the test database
        self.test_ejercicio = Ejercicio(nombre='Test Ejercicio', descripcion='Test Descripción', calorias=100)
        db.session.add(self.test_ejercicio)
        db.session.commit()

        # Check that the ejercicio instance has an id
        assert self.test_ejercicio.id is not None

        # Agregar entrenamiento a usuario\
        self.test_ejercicio = Ejercicio.query.first()
        self.entrenamiento = Entrenamiento(
            tiempo=datetime.strptime('00:10:00', '%H:%M:%S').time(),
            repeticiones=float(20),
            fecha=datetime.strptime('2023-03-10', '%Y-%m-%d').date(),
            ejercicio=int(self.test_ejercicio.id),
            persona=self.persona.id
        )

        # Create and commit a new Rutina instance to the test database
        self.test_rutina = Rutina(nombre='Test Rutina', descripcion='Test Descripción')
        db.session.add(self.test_rutina)
        db.session.commit()

        # Check that the Rutina instance has an id
        assert self.test_rutina.id is not None

        db.session.add(self.entrenamiento)
        db.session.commit()
        # Agregar rutina a usuario
        self.test_rutina = Rutina.query.first()
        self.entrenamiento_rutina = EntrenamientoRutina(
            tiempo=datetime.strptime('00:30:00', '%H:%M:%S').time(),
            repeticiones=float(30),
            fecha=datetime.strptime('2023-03-11', '%Y-%m-%d').date(),
            rutina=int(self.test_rutina.id),
            persona=self.persona.id
        )

        db.session.add(self.entrenamiento_rutina)
        db.session.commit()


    def tearDown(self):
        for persona_creada in self.personas_creadas:
            persona = Persona.query.get(persona_creada.id)
            db.session.delete(persona)
            db.session.commit()

        for usuario_creado in self.usuarios_creados:
            usuario_persona = Usuario.query.get(usuario_creado.id)
            db.session.delete(usuario_persona)
            db.session.commit()

        usuario_login = Usuario.query.get(self.usuario_id)
        db.session.delete(usuario_login)

        usuario_entrenador = Entrenador.query.get(self.entrenador_id)
        db.session.delete(usuario_entrenador)

        db.session.commit()

    def test_calcular_calorias_ejercicio(self):
        utilidad = UtilidadReporte()

        tiempo_segundos = (self.entrenamiento.tiempo.hour * 60 * 60) + (
                    self.entrenamiento.tiempo.minute * 60) + self.entrenamiento.tiempo.second
        conteo_calorico = ((4 * self.entrenamiento.repeticiones * self.entrenamiento.repeticiones * self.test_ejercicio.calorias) / tiempo_segundos)

        self.assertEqual(conteo_calorico, utilidad.calcular_calorias(self.entrenamiento))

    def test_calcular_calorias_rutina(self):
        utilidad = UtilidadReporte()
        conteo_calorico = 0
        for ejercicio in self.test_rutina.ejercicios:
            tiempo_segundos = self.entrenamiento_rutina.tiempo_segundos()
            conteo_calorico += utilidad.calorias_por_ejercicio(ejercicio, self.entrenamiento_rutina.repeticiones, tiempo_segundos)

        self.assertEqual(conteo_calorico, utilidad.calcular_calorias_rutina(self.entrenamiento_rutina))

    def test_reporte(self):
        # Datos prueba
        utilidad = UtilidadReporte()
        total_calorias = utilidad.calcular_calorias(self.entrenamiento) + utilidad.calcular_calorias_rutina(self.entrenamiento_rutina)
        # Definir endpoint, encabezados y hacer el llamado
        endpoint_persona = "/persona/" + str(self.persona.id) + "/reporte"
        headers = {'Content-Type': self.content_type, "Authorization": "Bearer {}".format(self.token)}

        reporte_persona = self.client.get(endpoint_persona,
                                            headers=headers)

        # Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta = json.loads(reporte_persona.get_data())
        totales = datos_respuesta['resultados'].pop()
        self.assertEqual(reporte_persona.status_code, 200)
        self.assertIsNotNone(datos_respuesta['resultados'])
        self.assertEqual(total_calorias, float(totales['calorias']))
        self.assertEqual(2, len(datos_respuesta['resultados']))

