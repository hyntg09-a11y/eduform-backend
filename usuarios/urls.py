"""
usuarios/urls.py — Equivalente a auth.routes.js

Express:                          Django:
router.post('/login', ...)    →   path('login/', login)
router.post('/register', ...) →   path('register/', register)
"""
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
]