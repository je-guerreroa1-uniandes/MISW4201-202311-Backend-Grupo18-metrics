from unittest import TestCase
from app import app, db
from modelos.modelos import Ejercicio, Rutina
from flask_jwt_extended import create_access_token
from faker import Faker

class TestRutinaViews(TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.db = db
        self.db.create_all()
        self.faker = Faker()

        # Set up a user and get a token
        self.access_token = create_access_token(identity={"username": "testuser"})

        # Create dummy data
        self.existing_rutina = Rutina(nombre='Test Rutina', descripcion='Descripción de prueba')
        self.db.session.add(self.existing_rutina)
        self.db.session.commit()
        self.existing_rutina_endpoint = f'/rutina/{self.existing_rutina.id}'
        self.rutinas_endpoint = '/rutinas'

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def test_get_rutina(self):
        response = self.client.get(self.existing_rutina_endpoint,
                                   headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 200)
        # Additional assertions for response data can be added here

    def test_delete_rutina(self):
        response = self.client.delete(self.existing_rutina_endpoint,
                                      headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 200)
        # Additional assertions to ensure deletion can be added here

    def test_get_rutinas(self):
        response = self.client.get(self.rutinas_endpoint,
                                   headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 200)
        # Additional assertions for response data can be added here

    def test_post_rutinas(self):
        data = {
            "nombre": "Nueva Rutina",
            "descripcion": "Descripción nueva",
            "ejercicios": []  # You would need to create some Ejercicio instances and add them here
        }
        response = self.client.post(self.rutinas_endpoint,
                                    json=data,
                                    headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 200)
        # Additional assertions for response data can be added here

    def test_put_rutinas(self):
        ejercicio = Ejercicio(nombre='Ejercicio 1', descripcion='Descripción ejercicio')
        self.db.session.add(ejercicio)
        self.db.session.commit()

        data = {
            "id": self.existing_rutina.id,
            "nombre": "Rutina Modificada",
            "descripcion": "Descripción modificada",
            "ejercicios": [{"id": ejercicio.id}]
        }
        response = self.client.put(self.rutinas_endpoint,
                                   json=data,
                                   headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 200)
        # Additional assertions for response data can be added here
