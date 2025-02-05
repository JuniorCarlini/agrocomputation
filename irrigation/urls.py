from django.urls import path
from .views import collect_environmental_data, collect_solenoid_state, get_data_fertil_state, collect_historico_fertil

urlpatterns = [
    # Api
    path('api/post-environmental/', collect_environmental_data, name='collect_environmental_data'),
    path('api/post-solenoid-state/', collect_solenoid_state, name='collect_solenoid_state'),
    path('api/get-fertilization-state/', get_data_fertil_state, name='get_data_fertil_state'),
    path('api/post-irrigation-state/', collect_historico_fertil, name='collect_historico_fertil'),

    # Templates
]