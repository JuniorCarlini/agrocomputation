from django.urls import path
from .views import (
    collect_environmental_data,
    collect_solenoid_state,
    get_data_fertil_state,
    collect_historico_fertil,
    dashboard_irrigation_view,
    temperature_chart_view,
    air_humidity_chart_view,
    soil_humidity_chart_view,
    water_usage_chart_view,
    fertil_usage_chart_view
)

urlpatterns = [
    # Api
    path('api/post-environmental/', collect_environmental_data, name='collect_environmental_data'),
    path('api/post-solenoid-state/', collect_solenoid_state, name='collect_solenoid_state'),
    path('api/get-fertilization-state/', get_data_fertil_state, name='get_data_fertil_state'),
    path('api/post-irrigation-state/', collect_historico_fertil, name='collect_historico_fertil'),
    
    # Templates
    path ('', dashboard_irrigation_view, name='dashboard_irrigation'),
    path ('temperature-chart/', temperature_chart_view, name='temperature_chart'),
    path ('air-humidity-chart/', air_humidity_chart_view, name='air_humidity_chart'),
    path ('soil-humidity-chart/', soil_humidity_chart_view, name='soil_humidity_chart'),
    path ('water-usage-chart/', water_usage_chart_view, name='water_usage_chart'),
    path ('fertil-usage-chart/', fertil_usage_chart_view, name='fertil_usage_chart'),

  ]