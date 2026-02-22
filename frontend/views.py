from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from frontend.encuestas import encuesta_socioeconomica, encuesta_vocacional
from frontend.motor_recomendacion import generar_recomendacion
from evaluaciones.models import EvaluacionVocacional, RespuestaEvaluacion, RecomendacionCarrera, Carrera


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
def test_view(request):
    step = int(request.POST.get('step', 1))
    index = int(request.POST.get('index', 0))
    preguntas = encuesta_socioeconomica if step == 1 else encuesta_vocacional
    respuestas_previas = {k[5:]: v for k, v in request.POST.items() if k.startswith('prev_')}

    if request.method == 'POST' and request.POST.get('accion') == 'siguiente':
        pregunta_actual = preguntas[index]
        valor = request.POST.get(f'respuesta_{pregunta_actual["id"]}', '')

        if not valor:
            return render(request, 'test.html', {
                'pregunta': pregunta_actual,
                'step': step,
                'index': index,
                'total': len(preguntas),
                'es_ultimo': step == 2 and index == len(preguntas) - 1,
                'respuestas_previas': respuestas_previas,
                'error': 'Debes seleccionar una opción'
            })

        respuestas_previas[pregunta_actual['id']] = valor

        if index < len(preguntas) - 1:
            index += 1
        elif step == 1:
            step = 2
            index = 0
            preguntas = encuesta_vocacional
        else:
            resultado = generar_recomendacion(respuestas_previas)

            evaluacion = EvaluacionVocacional.objects.create(
                idusuario=request.user,
                puntajetotal=0
            )

            for i, (preg_id, respuesta) in enumerate(respuestas_previas.items()):
                RespuestaEvaluacion.objects.create(
                    idevaluacion=evaluacion,
                    idpregunta=i,
                    respuesta=f"{preg_id}: {respuesta}"
                )

            carrera = Carrera.objects.filter(nombrecarrera=resultado['perfil']).first()
            if carrera:
                RecomendacionCarrera.objects.create(
                    idevaluacion=evaluacion,
                    idcarrera=carrera,
                    porcentajeafinidad=100,
                    justificacion=resultado['recomendacion']
                )

            request.session['resultado'] = resultado
            return redirect('dashboard')

    if request.method == 'POST' and request.POST.get('accion') == 'atras':
        if index > 0:
            index -= 1
        elif step == 2:
            step = 1
            index = len(encuesta_socioeconomica) - 1
            preguntas = encuesta_socioeconomica

    pregunta_actual = preguntas[index]
    return render(request, 'test.html', {
        'pregunta': pregunta_actual,
        'step': step,
        'index': index,
        'total': len(preguntas),
        'es_ultimo': step == 2 and index == len(preguntas) - 1,
        'respuestas_previas': respuestas_previas,
    })


@login_required(login_url='/')
def dashboard_view(request):
    resultado = request.session.get('resultado', None)

    evaluaciones = EvaluacionVocacional.objects.filter(
        idusuario=request.user
    ).order_by('-fecharealizacion')

    historial = []
    grafico = {}

    for ev in evaluaciones:
        rec = RecomendacionCarrera.objects.filter(idevaluacion=ev).first()
        if rec:
            perfil = rec.idcarrera.nombrecarrera
            historial.append({
                'fecha': ev.fecharealizacion,
                'perfil': perfil,
                'recomendacion': rec.justificacion
            })
            grafico[perfil] = grafico.get(perfil, 0) + 1

    grafico_labels = list(grafico.keys())
    grafico_datos = list(grafico.values())

    return render(request, 'dashboard.html', {
        'resultado': resultado,
        'usuario': request.user,
        'historial': historial,
        'grafico_labels': grafico_labels,
        'grafico_datos': grafico_datos,
    })
