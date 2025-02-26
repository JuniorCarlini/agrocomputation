from django.urls import path
from . import views

urlpatterns = [
    # Api
    path('api/post-weather-data/', views.collect_weather_data, name='collect_weather'),

    # Templates
    path ('', views.dashboard_station_view, name='dashboard_station'),
    path('dht-temperature-chart/', views.dht_temperature_chart_view, name='dht_temperature_chart'),
    path('bmp-temperature-chart/', views.bmp_temperature_chart_view, name='bmp_temperature_chart'),
    path('air-humidity-chart/', views.humidity_chart_view, name='air_humidity_chart'),
    path('pressure-chart/', views.pressure_chart_view, name='pressure_chart'),
    path('wind-speed-chart/', views.wind_speed_chart_view, name='wind_speed_chart'),
    path('wind-direction-chart/', views.wind_direction_chart_view, name='wind_direction_chart'),
    path('rainfall-chart/', views.rainfall_chart_view, name='rainfall_chart'),
    path('temperature-comparison-chart/', views.temperature_comparison_chart_view, name='temperature_comparison_chart'),


]