from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from frontend import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rutas de la App
    path('', views.home, name='home'),
    path('inicio/', views.home, name='inicio'), # Asumiendo que inicio es lo mismo que home
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # --- Rutas del Test Dinámico (CORREGIDAS) ---
    # 1. Ruta para INICIAR un nuevo test. No necesita ID.
    path('test/', views.test_view, name='test_start'),
    # 2. Ruta para CONTINUAR un test existente. Requiere ID.
    path('test/<int:evaluacion_id>/', views.test_view, name='test_view'),

    # Autenticación
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]