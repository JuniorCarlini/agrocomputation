from datetime import timedelta
from rest_framework import status
from django.utils import timezone
from django.shortcuts import render
from rest_framework.response import Response
from project.decorators import token_required
from .serializers import WeatherDataSerializer
from rest_framework.decorators import api_view
from .models import WeatherData, WeatherSummary

@api_view(['POST'])
@token_required
def collect_weather_data(request):
    serializer = WeatherDataSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Weather data recorded successfully"
        }, status=status.HTTP_201_CREATED)
    return Response({
        "error": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


def dashboard_station_view(request):
   hora_atual = timezone.now().hour
   imagem = 'icons/sol.png' if 6 <= hora_atual < 18 else 'icons/lua.png'
   
   try:
       # Último registro de dados meteorológicos
       ultimo_registro = WeatherData.objects.latest('timestamp')
       
       # Média temperatura
       temp_media = None
       if ultimo_registro.dht_temperature and ultimo_registro.bmp_temperature:
           temp_media = int(round((ultimo_registro.dht_temperature + ultimo_registro.bmp_temperature) / 2, 0))
       
       # Últimos 7 dias de chuva
       data_inicio = timezone.now() - timedelta(days=7)
       dados_chuva = WeatherData.objects.filter(
           timestamp__gte=data_inicio
       ).order_by('timestamp').values('timestamp', 'rainfall')
       
       dados_chuva_formatados = [
           {
               'data': registro['timestamp'].strftime('%d/%m'),
               'valor': registro['rainfall'] or 0
           }
           for registro in dados_chuva
       ]
       
       # Recuperar o último resumo meteorológico
       ultimo_resumo = WeatherSummary.objects.latest('created_at')
       
       context = {
           'imagem': imagem,
           'dados': {
               **ultimo_registro.__dict__,
               'humidity': int(ultimo_registro.humidity),
               'dht_temperature': int(round(ultimo_registro.dht_temperature, 0)),
               'bmp_temperature': int(round(ultimo_registro.bmp_temperature, 0))
           },
           'temperatura_media': temp_media,
           'dados_chuva': dados_chuva_formatados,
           
           # Adicionar dados do resumo meteorológico
           'resumo_meteorologico': {
               'temperatura_atual': ultimo_resumo.temperature_current,
               'temperatura_min': ultimo_resumo.temperature_min,
               'temperatura_max': ultimo_resumo.temperature_max,
               'umidade_atual': ultimo_resumo.humidity_current,
               'umidade_min': ultimo_resumo.humidity_min,
               'umidade_max': ultimo_resumo.humidity_max,
               'velocidade_vento': ultimo_resumo.wind_speed,
               'rajada_vento': ultimo_resumo.wind_gust_speed,
               'probabilidade_chuva': ultimo_resumo.rain_probability,
               'acumulado_chuva': ultimo_resumo.rain_accumulation
           }
       }
       
       return render(request, 'station/dashboard.html', context)
       
   except WeatherData.DoesNotExist:
       return render(request, 'station/dashboard.html', {
           'imagem': imagem,
           'erro': 'Nenhum dado meteorológico disponível.'
       })
   except WeatherSummary.DoesNotExist:
       return render(request, 'station/dashboard.html', {
           'imagem': imagem,
           'erro': 'Nenhum resumo meteorológico disponível.'
       })
   except Exception as e:
       return render(request, 'station/dashboard.html', {
           'imagem': imagem,
           'erro': f'Erro ao carregar dados: {str(e)}'
       })
       