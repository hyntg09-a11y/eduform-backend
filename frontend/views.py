from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import Http404
from evaluaciones.models import Pregunta, OpcionRespuesta, Evaluacion, RespuestaUsuario


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
    # --- Iniciar un nuevo test (si no hay ID) ---
    if evaluacion_id is None:
        nueva_evaluacion = Evaluacion.objects.create(usuario=request.user)
        return redirect('test_view', evaluacion_id=nueva_evaluacion.id)

    # --- Cargar la evaluación actual ---
    try:
        evaluacion = Evaluacion.objects.get(id=evaluacion_id, usuario=request.user)
    except Evaluacion.DoesNotExist:
        raise Http404("Evaluación no encontrada o no pertenece al usuario.")

    # --- Procesar respuesta enviada (POST) ---
    if request.method == 'POST':
        opcion_id = request.POST.get('opcion_id')
        pregunta_id = request.POST.get('pregunta_id')
        
        if not opcion_id or not pregunta_id:
            # Idealmente, manejar este error de forma más elegante en el template
            return redirect('test_view', evaluacion_id=evaluacion.id)

        try:
            opcion_seleccionada = OpcionRespuesta.objects.get(id=opcion_id, pregunta_id=pregunta_id)
            pregunta_actual = Pregunta.objects.get(id=pregunta_id)
        except (OpcionRespuesta.DoesNotExist, Pregunta.DoesNotExist):
            raise Http404("La opción o pregunta no es válida.")

        # Guardar o actualizar la respuesta para esta pregunta en esta evaluación
        RespuestaUsuario.objects.update_or_create(
            evaluacion=evaluacion,
            opcion_seleccionada__pregunta=pregunta_actual,
            defaults={'opcion_seleccionada': opcion_seleccionada}
        )

    # --- Lógica para encontrar la siguiente pregunta ---
    preguntas_totales = Pregunta.objects.all()
    preguntas_respondidas_ids = set(
        evaluacion.respuestas.values_list('opcion_seleccionada__pregunta_id', flat=True)
    )

    siguiente_pregunta = None
    for pregunta in preguntas_totales:
        if pregunta.id not in preguntas_respondidas_ids:
            siguiente_pregunta = pregunta
            break
    
    # --- Finalizar el test si no hay más preguntas ---
    if siguiente_pregunta is None:
        resultado = evaluacion.calcular_resultado()
        # Guardamos el resultado en la sesión para mostrarlo inmediatamente en el dashboard
        if resultado:
            request.session['resultado_reciente'] = {
                'perfil': resultado.nombre,
                'recomendacion': resultado.descripcion
            }
        return redirect('dashboard')

    # --- Renderizar la siguiente pregunta ---
    progreso = (len(preguntas_respondidas_ids) / preguntas_totales.count()) * 100 if preguntas_totales.count() > 0 else 0

    context = {
        'evaluacion': evaluacion,
        'pregunta': siguiente_pregunta,
        'progreso': round(progreso)
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
