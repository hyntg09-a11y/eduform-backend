from django.db import models
from django.conf import settings


class Pregunta(models.Model):
    """
    Modelo para representar una pregunta del test vocacional.
    """
    idpregunta = models.AutoField(primary_key=True)
    texto = models.TextField()

    class Meta:
        db_table = 'pregunta' # Assuming a table named 'pregunta' in your DB

    def __str__(self):
        return self.texto


class OpcionRespuesta(models.Model):
    idopcion = models.AutoField(primary_key=True)
    # Relación ForeignKey: Una opción pertenece a una sola pregunta.
    # related_name='opciones' permite acceder desde Pregunta así: pregunta_obj.opciones.all()
    idpregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, db_column='idpregunta', related_name='opciones')
    texto = models.TextField()

    class Meta:
        db_table = 'opcionrespuesta' # Assuming a table named 'opcionrespuesta' in your DB

    def __str__(self):
        return self.texto


# ─── MODELOS PARA EL FRONTEND CON DJANGO TEMPLATES ───────────────────────────────
# Estos modelos son utilizados por `frontend/views.py` para el test dinámico
# y el dashboard renderizados en el servidor.

class PerfilVocacional(models.Model):
    """
    Representa un perfil vocacional (ej. Artista, Investigador) que es el
    resultado de una evaluación.
    """
    idperfil = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()

    class Meta:
        db_table = 'perfilvocacional'

    def __str__(self):
        return self.nombre


class Evaluacion(models.Model):
    """
    Representa una instancia de un test realizado por un usuario.
    """
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    perfil_resultado = models.ForeignKey(
        PerfilVocacional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='idperfil'
    )

    class Meta:
        db_table = 'evaluacion'

    def __str__(self):
        return f"Evaluación de {self.usuario.username} en {self.fecha_creacion.strftime('%Y-%m-%d')}"

    def calcular_resultado(self):
        """
        Calcula el perfil vocacional basado en las respuestas.
        
        IMPORTANTE: Esta es una lógica de ejemplo y debe ser reemplazada por el algoritmo real.
        Para que funcione, DEBE HABER al menos un registro en la tabla `perfilvocacional`.
        Puedes agregar perfiles desde el panel de administrador de Django.
        """
        # TODO: Implementar la lógica real de cálculo de resultados basada en las respuestas del usuario.
        # Por ahora, asigna el primer perfil que encuentre como demostración.
        perfil = PerfilVocacional.objects.first()
        if perfil:
            self.perfil_resultado = perfil
            self.save()
        return self.perfil_resultado


class RespuestaUsuario(models.Model):
    id = models.AutoField(primary_key=True)

    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.CASCADE,
        related_name='respuestas'
    )

    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    opcion_seleccionada = models.ForeignKey(
        OpcionRespuesta,
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'respuestausuario'

        constraints = [
            models.UniqueConstraint(
                fields=['evaluacion', 'pregunta'],
                name='respuesta_unica_por_pregunta'
            )
        ]

    def __str__(self):
        # El campo `pregunta` puede ser nulo, por lo que obtenemos el PK de forma segura
        # a través de la opción seleccionada si es necesario.
        pregunta_pk = self.pregunta.pk if self.pregunta else self.opcion_seleccionada.idpregunta.pk
        return f"Eval {self.evaluacion.pk} - Pregunta {pregunta_pk}"
