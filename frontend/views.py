from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

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
