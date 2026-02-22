"""
evaluaciones/views.py — Equivalente a:
  - evaluacion.controller.js  (finalizarEvaluacion)
  - dashboard.controller.js   (getDashboard)

VERSIÓN CORREGIDA

Mapeo de queries SQL → Django ORM:
  INSERT INTO evaluacionvocacional     → EvaluacionVocacional.objects.create()
  INSERT INTO respuestasevaluacion     → RespuestaEvaluacion.objects.create()
  SELECT idcarrera FROM carrera        → Carrera.objects.get()
  INSERT INTO recomendacincarrera      → RecomendacionCarrera.objects.create()
  SELECT ... GROUP BY nombrecarrera    → RecomendacionCarrera.objects.filter().values()
  SELECT ... ORDER BY fecha DESC       → RecomendacionCarrera.objects.filter().order_by()
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .models import EvaluacionVocacional, RespuestaEvaluacion, Carrera, RecomendacionCarrera
from usuarios.models import Usuario


# ─── MAPA DE PERFILES ──────────────────────────────────────────────────────────
# Exactamente igual que mapaCarreras en evaluacion.controller.js
MAPA_CARRERAS = {
    'Tecnologia': 'Ingeniería de Sistemas',
    'Salud': 'Enfermería',
    'Educacion': 'Licenciatura en Educación',
    'Arte': 'Diseño Gráfico',
    'Negocios': 'Administración de Empresas',
}


@api_view(['POST'])
def finalizar_evaluacion(request):
    """
    POST /api/evaluacion/finalizar
    Equivalente exacto a finalizarEvaluacion en evaluacion.controller.js

    Body: { idusuario, respuestas: {id: valor, ...}, recomendacion: {perfil, recomendacion} }
    """
    idusuario = request.data.get('idusuario')
    respuestas = request.data.get('respuestas', {})
    recomendacion = request.data.get('recomendacion')

    if not idusuario or not recomendacion:
        return Response({'error': 'Datos incompletos'}, status=status.HTTP_400_BAD_REQUEST)

    # Equivalente a: INSERT INTO evaluacionvocacional (idusuario, fecharealizacion, puntajetotal) VALUES (?, NOW(), ?)
    try:
        usuario = Usuario.objects.get(idusuario=idusuario)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)

    evaluacion = EvaluacionVocacional.objects.create(
        idusuario=usuario,
        puntajetotal=0
    )

    # Equivalente al for loop: INSERT INTO respuestasevaluacion ...
    for idpregunta, respuesta in respuestas.items():
        RespuestaEvaluacion.objects.create(
            idevaluacion=evaluacion,
            idpregunta=idpregunta,
            respuesta=respuesta
        )

    # Equivalente a: mapaCarreras[recomendacion.perfil]
    nombre_carrera = MAPA_CARRERAS.get(recomendacion.get('perfil'))
    if not nombre_carrera:
        return Response({'error': 'Perfil no reconocido'}, status=status.HTTP_400_BAD_REQUEST)

    # Equivalente a: SELECT idcarrera FROM carrera WHERE nombrecarrera = ? LIMIT 1
    try:
        carrera = Carrera.objects.get(nombrecarrera=nombre_carrera)
    except Carrera.DoesNotExist:
        return Response({'error': 'Carrera no encontrada en base de datos'}, status=status.HTTP_400_BAD_REQUEST)

    # Equivalente a: INSERT INTO recomendacincarrera (idevaluacion, idcarrera, porcentajeafinidad, justificacion, fecharecomendacion)
    RecomendacionCarrera.objects.create(
        idevaluacion=evaluacion,
        idcarrera=carrera,
        porcentajeafinidad=100,
        justificacion=recomendacion.get('recomendacion', '')
    )

    return Response({'ok': True})


@api_view(['GET'])
def get_dashboard(request, idusuario):
    """
    GET /api/dashboard/<idusuario>
    Equivalente exacto a getDashboard en dashboard.controller.js

    Respuesta: { grafico: [{perfil, cantidad}], historial: [{fecha, perfil, recomendacion}] }
    — Misma estructura que consume DashboardResultados.jsx
    """
    # ─── GRÁFICO ───────────────────────────────────────────────────────────────
    # Equivalente a la query SQL con GROUP BY nombrecarrera:
    # SELECT c.nombrecarrera AS perfil, COUNT(*) AS cantidad
    # FROM recomendacincarrera r
    # JOIN evaluacionvocacional e ON r.idevaluacion = e.idevaluacion
    # JOIN carrera c ON r.idcarrera = c.idcarrera
    # WHERE e.idusuario = ?
    # GROUP BY c.nombrecarrera

    grafico_qs = (
        RecomendacionCarrera.objects
        .filter(idevaluacion__idusuario=idusuario)
        .values('idcarrera__nombrecarrera')
        .annotate(cantidad=Count('idcarrera'))
    )

    grafico = [
        {
            'perfil': item['idcarrera__nombrecarrera'],
            'cantidad': item['cantidad']
        }
        for item in grafico_qs
    ]

    # ─── HISTORIAL ─────────────────────────────────────────────────────────────
    # Equivalente a:
    # SELECT e.fecharealizacion AS fecha, c.nombrecarrera AS perfil, r.justificacion AS recomendacion
    # FROM recomendacincarrera r
    # JOIN evaluacionvocacional e ON r.idevaluacion = e.idevaluacion
    # JOIN carrera c ON r.idcarrera = c.idcarrera
    # WHERE e.idusuario = ?
    # ORDER BY e.fecharealizacion DESC

    historial_qs = (
        RecomendacionCarrera.objects
        .filter(idevaluacion__idusuario=idusuario)
        .select_related('idevaluacion', 'idcarrera')
        .order_by('-idevaluacion__fecharealizacion')
    )

    historial = [
        {
            'fecha': r.idevaluacion.fecharealizacion,
            'perfil': r.idcarrera.nombrecarrera,
            'recomendacion': r.justificacion
        }
        for r in historial_qs
    ]

    return Response({'grafico': grafico, 'historial': historial})


# Helper para values() con alias
def models_value(field):
    from django.db.models import F
    return F(field)

