from django.contrib import admin
from users.views import login_view
from django.urls import path, include
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

