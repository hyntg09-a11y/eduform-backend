from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Pregunta, OpcionRespuesta, Evaluacion, RespuestaUsuario

User = get_user_model()

class EvaluacionTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="123456"
        )

        self.pregunta = Pregunta.objects.create(
            texto="¿Te gusta programar?"
        )

        self.opcion = OpcionRespuesta.objects.create(
            idpregunta=self.pregunta,
            texto="Sí"
        )

    def test_crear_evaluacion(self):

        evaluacion = Evaluacion.objects.create(
            usuario=self.user
        )

        respuesta = RespuestaUsuario.objects.create(
            evaluacion=evaluacion,
            opcion_seleccionada=self.opcion
        )

        self.assertEqual(
            evaluacion.respuestas.count(),
            1
        )
