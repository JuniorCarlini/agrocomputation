from django.urls import path, include
from comum.views import apresentation_view, configuration_view

urlpatterns = [
    path('', apresentation_view, name='apresentation'),
    path('configuration/', configuration_view, name='configuration'),
]
