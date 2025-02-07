from django.urls import path
from .views import collect_weather_data, dashboard_station_view

urlpatterns = [
    # Api
    path('api/post-weather-data/', collect_weather_data, name='collect_weather'),

    # Templates
    path ('', dashboard_station_view, name='dashboard_station'),
    

]