from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import Http404
from evaluaciones.models import Pregunta, OpcionRespuesta, Evaluacion, RespuestaUsuario, PerfilVocacional
from django.db.models import Count


@ensure_csrf_cookie
def home(request):
    return render(request, 'home.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('home')
        return render(request, 'home.html', {'login_error': 'Credenciales incorrectas'})
    return redirect('home')


def register_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=email).exists():
            return render(request, 'home.html', {'registro_error': 'El correo ya está registrado'})
        user = User.objects.create_user(username=email, email=email, password=password, first_name=nombre)
        login(request, user)
        return redirect('home')
    return redirect('home')


@login_required(login_url='/')
def test_view(request, evaluacion_id=None):
    # --- 1. Lógica para Iniciar o Reanudar un Test ---
    if evaluacion_id is None:
        # Buscar una evaluación activa (sin resultado) para el usuario.
        evaluacion_activa = Evaluacion.objects.filter(
            usuario=request.user,
            perfil_resultado__isnull=True
        ).order_by('-fecha_creacion').first()

        if evaluacion_activa:
            # Si existe una evaluación en curso, redirigir a ella.
            return redirect('test_view', evaluacion_id=evaluacion_activa.id)
        
        # Si no hay ninguna activa, crear una nueva.
        nueva_evaluacion = Evaluacion.objects.create(usuario=request.user)
        return redirect('test_view', evaluacion_id=nueva_evaluacion.id)

    # --- 2. Cargar la evaluación actual ---
    try:
        evaluacion = Evaluacion.objects.get(id=evaluacion_id, usuario=request.user)
    except Evaluacion.DoesNotExist:
        raise Http404("Evaluación no encontrada o no pertenece al usuario.")

    # --- 3. Procesar respuesta enviada (POST) ---
    if request.method == 'POST':
        opcion_id = request.POST.get('opcion_id')
        pregunta_id = request.POST.get('pregunta_id')
        
        if opcion_id and pregunta_id:
            try:
                opcion_seleccionada = OpcionRespuesta.objects.get(idopcion=opcion_id, idpregunta_id=pregunta_id)
                
                # Borrar respuesta anterior si existe (para evitar duplicados si el usuario retrocede)
                RespuestaUsuario.objects.filter(
                    evaluacion=evaluacion,
                    opcion_seleccionada__idpregunta_id=pregunta_id
                ).delete()
                
                # Guardar nueva respuesta
                RespuestaUsuario.objects.create(evaluacion=evaluacion, opcion_seleccionada=opcion_seleccionada)
                
                # Patrón PRG (Post-Redirect-Get): Redirigir para evitar reenvío de formulario
                return redirect('test_view', evaluacion_id=evaluacion.id)
                
            except (OpcionRespuesta.DoesNotExist, Pregunta.DoesNotExist):
                pass # Ignorar datos inválidos o manejar error
        
        # Si falla algo, redirigir al mismo punto
        return redirect('test_view', evaluacion_id=evaluacion.id)

    # --- 4. Lógica para encontrar la siguiente pregunta (ROBUSTA Y OPTIMIZADA) ---
    # Define un queryset base de preguntas válidas (con al menos una opción) para reutilizar.
    preguntas_validas_qs = Pregunta.objects.annotate(
        num_opciones=Count('opciones')
    ).filter(num_opciones__gt=0)

    # Obtiene los IDs de las preguntas ya respondidas para esta evaluación.
    preguntas_respondidas_ids = list(
        evaluacion.respuestas.values_list('opcion_seleccionada__idpregunta_id', flat=True)
    )

    # Busca la siguiente pregunta válida y no respondida.
    # prefetch_related('opciones') evita una consulta extra en la plantilla (N+1 problem).
    siguiente_pregunta = preguntas_validas_qs.exclude(
        idpregunta__in=preguntas_respondidas_ids
    ).order_by('idpregunta').prefetch_related('opciones').first()

    # --- 5. Finalizar el test si no hay más preguntas ---
    if siguiente_pregunta is None:
        resultado = evaluacion.calcular_resultado()
        # Guardamos el resultado en la sesión para mostrarlo inmediatamente en el dashboard
        if resultado:
            request.session['resultado_reciente'] = {
                'perfil': resultado.nombre,
                'recomendacion': resultado.descripcion
            }
        return redirect('dashboard')

    # --- 6. Renderizar la siguiente pregunta ---
    # El total de preguntas ahora se basa en las preguntas válidas para un progreso preciso.
    total_preguntas = preguntas_validas_qs.count()
    pregunta_actual_num = len(preguntas_respondidas_ids) + 1
    progreso = ((pregunta_actual_num - 1) / total_preguntas) * 100 if total_preguntas > 0 else 0

    context = {
        'evaluacion': evaluacion,
        'pregunta': siguiente_pregunta,
        'progreso': round(progreso),
        'pregunta_actual_num': pregunta_actual_num,
        'total_preguntas': total_preguntas
    }
    return render(request, 'test_dinamico.html', context)


@login_required(login_url='/')
def dashboard_view(request):
    # Usamos pop para obtener el resultado y limpiarlo de la sesión, evitando que se muestre en futuras visitas.
    resultado_reciente = request.session.pop('resultado_reciente', None)

    # Obtenemos el historial desde la base de datos, ahora basado en el nuevo modelo Evaluacion
    evaluaciones_pasadas = Evaluacion.objects.filter(
        usuario=request.user,
        perfil_resultado__isnull=False
    ).select_related('perfil_resultado').order_by('-fecha_creacion')

    historial = []
    grafico = {}

    for ev in evaluaciones_pasadas:
        perfil = ev.perfil_resultado
        historial.append({
            'fecha': ev.fecha_creacion,
            'perfil': perfil.nombre,
            'recomendacion': perfil.descripcion
        })
        grafico[perfil.nombre] = grafico.get(perfil.nombre, 0) + 1

    grafico_labels = list(grafico.keys())
    grafico_datos = list(grafico.values())

    return render(request, 'dashboard.html', {
        'resultado': resultado_reciente, # El resultado del test que acabamos de hacer
        'usuario': request.user,
        'historial': historial,
        'grafico_labels': grafico_labels,
        'grafico_datos': grafico_datos,
    })
