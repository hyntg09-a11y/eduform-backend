"""
evaluaciones/models.py — Equivalente a las tablas MySQL usadas en:
  - evaluacion.controller.js
  - dashboard.controller.js

Tablas mapeadas:
  evaluacionvocacional    → EvaluacionVocacional
  respuestasevaluacion    → RespuestaEvaluacion
  carrera                 → Carrera
  recomendacincarrera     → RecomendacionCarrera  (sí, sin 'o', igual que tu BD)
"""

from django.db import models
from django.conf import settings


class Carrera(models.Model):
    idcarrera = models.AutoField(primary_key=True)
    nombrecarrera = models.CharField(max_length=100, null=True)
    duracionvalor = models.IntegerField(null=True)
    duracionunidad = models.CharField(max_length=20, null=True)
    nivelacademico = models.CharField(max_length=50, null=True)
    class Meta:
        db_table = 'carrera'

    def __str__(self):
        return self.nombrecarrera


class EvaluacionVocacional(models.Model):
    """
    Tabla: evaluacionvocacional
    Usada en: INSERT INTO evaluacionvocacional (idusuario, fecharealizacion, puntajetotal)
    """
    idevaluacion = models.AutoField(primary_key=True)
    idusuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='idusuario'
    )
    fecharealizacion = models.DateTimeField(auto_now_add=True)
    puntajetotal = models.IntegerField(default=0)

    class Meta:
        db_table = 'evaluacionvocacional'


class RespuestaEvaluacion(models.Model):
    idrespuesta = models.AutoField(primary_key=True)
    idevaluacion = models.ForeignKey(EvaluacionVocacional, on_delete=models.CASCADE, db_column='idevaluacion')
    idpregunta = models.IntegerField(default=0)  # int en tu BD original
    respuesta = models.TextField(null=True)
    class Meta:
        db_table = 'respuestasevaluacion'


class RecomendacionCarrera(models.Model):
    idrecomendacion = models.AutoField(primary_key=True)
    idevaluacion = models.ForeignKey(EvaluacionVocacional,on_delete=models.CASCADE, db_column='idevaluacion')
    idcarrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, db_column='idcarrera')
    porcentajeafinidad = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    justificacion = models.TextField(null=True)
    fecharecomendacion = models.DateTimeField(null=True)
    idprioridad = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'recomendacincarrera'
