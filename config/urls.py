from django.contrib import admin
from django.urls import path
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from frontend.views import home, login_view, register_view, test_view, dashboard_view

def logout_view(request):
    auth_logout(request)
    return redirect('home')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('registro/', register_view, name='registro'),
    path('logout/', logout_view, name='logout'),
    path('test/', test_view, name='test_inicio'), # Inicia un nuevo test
    path('test/<int:evaluacion_id>/', test_view, name='test_view'), # Continúa un test existente
    path('dashboard/', dashboard_view, name='dashboard'),
]
