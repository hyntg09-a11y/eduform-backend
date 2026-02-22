"""
evaluaciones/urls.py — Equivalente a dashboard.routes.js + evaluacion.routes.js

Express:                                  Django:
router.get('/dashboard/:idusuario')   →   path('dashboard/<int:idusuario>/', get_dashboard)
router.post('/evaluacion/finalizar')  →   path('evaluacion/finalizar/', finalizar_evaluacion)
"""

from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/<int:idusuario>/', views.get_dashboard, name='dashboard'),
    path('evaluacion/finalizar/', views.finalizar_evaluacion, name='finalizar_evaluacion'),
]
