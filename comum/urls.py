from django.urls import path, include
from comum.views import apresentation_view

urlpatterns = [
    path('', apresentation_view, name='apresentation'),
]
