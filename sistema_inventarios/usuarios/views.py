from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .models import Usuario
from django.contrib import messages

def registro(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            usuario = Usuario.objects.create_user(
                username=email,  # Usamos email como username
                email=email,
                password=password,
                first_name=nombre
            )
            login(request, usuario)
            return redirect('home')  # Redirigir a la página principal
        except Exception as e:
            messages.error(request, f'Error en el registro: {str(e)}')
    
    return render(request, 'auth/registro.html')

def iniciar_sesion(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Credenciales inválidas')
    
    return render(request, 'auth/login.html')

def home(request):
    return render(request, 'home.html')