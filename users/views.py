from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.user.is_authenticated:
        return redirect("configuration")
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('configuration')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'users/login.html')

def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)
