from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'users/login.html')

def about_view(request):
    return render(request, 'about/about.html')

def custom_404(request, exception=None):
    context = {}
    response = render(request, 'errors/404.html', context)
    response.status_code = 404
    return response

def home(request):
    return render(request, 'home.html')
