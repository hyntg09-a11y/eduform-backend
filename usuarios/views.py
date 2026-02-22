"""
usuarios/views.py — Equivalente exacto a auth.controller.js

Express → Django:
  bcrypt.hash()           → user.set_password()  (Django maneja bcrypt)
  bcrypt.compare()        → authenticate()
  jwt.sign()              → RefreshToken.for_user()
  db.execute(SELECT...)   → Usuario.objects.get()
  db.execute(INSERT...)   → Usuario.objects.create_user()

Respuestas JSON idénticas a las que espera tu React:
  { token, usuario: { id, nombre, email } }
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Usuario


def get_tokens_for_user(user):
    """
    Equivalente a:
    jwt.sign({ id: usuario.idusuario, email: usuario.email }, 'CLAVE_SECRETA', { expiresIn: '1d' })
    """
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@api_view(['POST'])
def register(request):
    """
    POST /api/auth/register
    Equivalente a exports.register en auth.controller.js
    
    Body: { nombre, email, password }
    """
    nombre = request.data.get('nombre')
    email = request.data.get('email')
    password = request.data.get('password')

    # Equivalente a: SELECT idusuario FROM usuario WHERE email = ?
    if Usuario.objects.filter(email=email).exists():
        return Response(
            {'error': 'El correo ya está registrado'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Equivalente a: bcrypt.hash() + INSERT INTO usuario
    user = Usuario.objects.create_user(
        email=email,
        nombre=nombre,
        password=password
    )

    return Response({'ok': True})


@api_view(['POST'])
def login(request):
    """
    POST /api/auth/login
    Equivalente a exports.login en auth.controller.js

    Body: { email, password }
    Respuesta: { token, usuario: { id, nombre, email } }
    — Misma estructura que espera tu React en localStorage
    """
    email = request.data.get('email')
    password = request.data.get('password')

    # Equivalente a: SELECT * FROM usuario WHERE email = ?
    try:
        user = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no existe'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Equivalente a: bcrypt.compare(password, usuario.password)
    user = authenticate(request, username=email, password=password)
    if user is None:
        return Response(
            {'error': 'Contraseña incorrecta'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Equivalente a: jwt.sign({id, email}, 'CLAVE_SECRETA', {expiresIn: '1d'})
    token = get_tokens_for_user(user)

    # Respuesta idéntica a la que espera tu React
    return Response({
        'token': token,
        'usuario': {
            'id': user.idusuario,    # React usa usuario.id → localStorage
            'nombre': user.nombre,
            'email': user.email
        }
    })
