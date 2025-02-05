from django.urls import path
from .views import collect_weather_data

urlpatterns = [
    # Api
    path('api/post-weather-data/', collect_weather_data, name='collect_weather'),

    # Templates
]