from datetime import timedelta
from rest_framework import status
from django.utils import timezone
from django.shortcuts import render
from rest_framework.response import Response
from project.decorators import token_required
from .serializers import WeatherDataSerializer
from django.http import HttpResponseBadRequest
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

# Dashboard view
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
        
        # Últimos 7 registros diários de chuva (um por dia)
        from django.db.models import Sum, Max
        from django.db.models.functions import TruncDate
        
        # Agrupa dados por dia e soma as precipitações
        precipitacao_diaria = WeatherData.objects.annotate(
            dia=TruncDate('timestamp')
        ).values('dia').annotate(
            total_chuva=Sum('rainfall'),
            ultima_hora=Max('timestamp')
        ).order_by('-dia')[:7]
        
        # Inverte a ordem para exibir do mais antigo para o mais recente
        precipitacao_diaria = list(reversed(precipitacao_diaria))
        
        dados_chuva_formatados = [
            {
                'data': registro['dia'].strftime('%d/%m'),
                'valor': registro['total_chuva'] or 0
            }
            for registro in precipitacao_diaria
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

# Temperatura DHT chart view
def dht_temperature_chart_view(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fim = request.GET.get('hora_fim')

    if data_inicio and data_fim and hora_inicio and hora_fim:
        try:
            start_datetime = timezone.datetime.fromisoformat(f"{data_inicio} {hora_inicio}")
            end_datetime = timezone.datetime.fromisoformat(f"{data_fim} {hora_fim}")

            # Converte de UTC para o horário local do Django
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)

            # Filtra os dados no banco de dados
            data = WeatherData.objects.filter(
                timestamp__range=[start_datetime, end_datetime],
                dht_temperature__isnull=False
            ).order_by('timestamp')
        except ValueError:
            return HttpResponseBadRequest("Data ou hora em formato inválido.")
    else:
        # Pega os últimos 20 registros por padrão
        data = WeatherData.objects.filter(
            dht_temperature__isnull=False
        ).order_by('-timestamp')[:20]
        # Inverte para exibir em ordem cronológica
        data = list(reversed(data))

    context = {
        'labels': [timezone.localtime(d.timestamp).strftime('%d/%m/%Y %H:%M') for d in data],
        'dht_temperature_data': [d.dht_temperature for d in data],
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'hora_inicio': hora_inicio,
        'hora_fim': hora_fim,
    }

    return render(request, 'station/dht_temperature_chart.html', context)

# Temperatura BMP chart view
def bmp_temperature_chart_view(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fim = request.GET.get('hora_fim')

    if data_inicio and data_fim and hora_inicio and hora_fim:
        try:
            start_datetime = timezone.datetime.fromisoformat(f"{data_inicio} {hora_inicio}")
            end_datetime = timezone.datetime.fromisoformat(f"{data_fim} {hora_fim}")

            # Converte de UTC para o horário local do Django
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)

            # Filtra os dados no banco de dados
            data = WeatherData.objects.filter(
                timestamp__range=[start_datetime, end_datetime],
                bmp_temperature__isnull=False
            ).order_by('timestamp')
        except ValueError:
            return HttpResponseBadRequest("Data ou hora em formato inválido.")
    else:
        # Pega os últimos 20 registros por padrão
        data = WeatherData.objects.filter(
            bmp_temperature__isnull=False
        ).order_by('-timestamp')[:20]
        # Inverte para exibir em ordem cronológica
        data = list(reversed(data))

    context = {
        'labels': [timezone.localtime(d.timestamp).strftime('%d/%m/%Y %H:%M') for d in data],
        'bmp_temperature_data': [d.bmp_temperature for d in data],
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'hora_inicio': hora_inicio,
        'hora_fim': hora_fim,
    }

    return render(request, 'station/bmp_temperature_chart.html', context)

# Umidade chart view
def humidity_chart_view(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fim = request.GET.get('hora_fim')

    if data_inicio and data_fim and hora_inicio and hora_fim:
        try:
            start_datetime = timezone.datetime.fromisoformat(f"{data_inicio} {hora_inicio}")
            end_datetime = timezone.datetime.fromisoformat(f"{data_fim} {hora_fim}")

            # Converte de UTC para o horário local do Django
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)

            # Filtra os dados no banco de dados
            data = WeatherData.objects.filter(
                timestamp__range=[start_datetime, end_datetime],
                humidity__isnull=False
            ).order_by('timestamp')
        except ValueError:
            return HttpResponseBadRequest("Data ou hora em formato inválido.")
    else:
        # Pega os últimos 20 registros por padrão
        data = WeatherData.objects.filter(
            humidity__isnull=False
        ).order_by('-timestamp')[:20]
        # Inverte para exibir em ordem cronológica
        data = list(reversed(data))

    context = {
        'labels': [timezone.localtime(d.timestamp).strftime('%d/%m/%Y %H:%M') for d in data],
        'air_humidity_data': [d.humidity for d in data],
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'hora_inicio': hora_inicio,
        'hora_fim': hora_fim,
    }

    return render(request, 'station/air_humidity_chart.html', context)

# Pressão chart view
def pressure_chart_view(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fim = request.GET.get('hora_fim')

    if data_inicio and data_fim and hora_inicio and hora_fim:
        try:
            start_datetime = timezone.datetime.fromisoformat(f"{data_inicio} {hora_inicio}")
            end_datetime = timezone.datetime.fromisoformat(f"{data_fim} {hora_fim}")

            # Converte de UTC para o horário local do Django
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)

            # Filtra os dados no banco de dados
            data = WeatherData.objects.filter(
                timestamp__range=[start_datetime, end_datetime],
                pressure__isnull=False
            ).order_by('timestamp')
        except ValueError:
            return HttpResponseBadRequest("Data ou hora em formato inválido.")
    else:
        # Pega os últimos 20 registros por padrão
        data = WeatherData.objects.filter(
            pressure__isnull=False
        ).order_by('-timestamp')[:20]
        # Inverte para exibir em ordem cronológica
        data = list(reversed(data))

    context = {
        'labels': [timezone.localtime(d.timestamp).strftime('%d/%m/%Y %H:%M') for d in data],
        'pressure_data': [d.pressure for d in data],
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'hora_inicio': hora_inicio,
        'hora_fim': hora_fim,
    }

    return render(request, 'station/pressure_chart.html', context)

# Velocidade do Vento chart view
def wind_speed_chart_view(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fim = request.GET.get('hora_fim')

    if data_inicio and data_fim and hora_inicio and hora_fim:
        try:
            start_datetime = timezone.datetime.fromisoformat(f"{data_inicio} {hora_inicio}")
            end_datetime = timezone.datetime.fromisoformat(f"{data_fim} {hora_fim}")

            # Converte de UTC para o horário local do Django
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)

            # Filtra os dados no banco de dados
            data = WeatherData.objects.filter(
                timestamp__range=[start_datetime, end_datetime],
                wind_speed__isnull=False
            ).order_by('timestamp')
        except ValueError:
            return HttpResponseBadRequest("Data ou hora em formato inválido.")
    else:
        # Pega os últimos 20 registros por padrão
        data = WeatherData.objects.filter(
            wind_speed__isnull=False
        ).order_by('-timestamp')[:20]
        # Inverte para exibir em ordem cronológica
        data = list(reversed(data))

    context = {
        'labels': [timezone.localtime(d.timestamp).strftime('%d/%m/%Y %H:%M') for d in data],
        'wind_speed_data': [d.wind_speed for d in data],
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'hora_inicio': hora_inicio,
        'hora_fim': hora_fim,
    }

    return render(request, 'station/wind_speed_chart.html', context)

# Direção do vento chart view
def wind_direction_chart_view(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fim = request.GET.get('hora_fim')

    if data_inicio and data_fim and hora_inicio and hora_fim:
        try:
            start_datetime = timezone.datetime.fromisoformat(f"{data_inicio} {hora_inicio}")
            end_datetime = timezone.datetime.fromisoformat(f"{data_fim} {hora_fim}")

            # Converte de UTC para o horário local do Django
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)

            # Filtra os dados no banco de dados
            data = WeatherData.objects.filter(
                timestamp__range=[start_datetime, end_datetime],
                wind_direction__isnull=False
            ).order_by('timestamp')
        except ValueError:
            return HttpResponseBadRequest("Data ou hora em formato inválido.")
    else:
        # Pega os últimos 20 registros por padrão
        data = WeatherData.objects.filter(
            wind_direction__isnull=False
        ).order_by('-timestamp')[:20]
        # Inverte para exibir em ordem cronológica
        data = list(reversed(data))

    # Para direção do vento, vamos converter os códigos para nomes completos
    wind_direction_map = {code: name for code, name in WeatherData.WIND_DIRECTIONS}
    
    context = {
        'labels': [timezone.localtime(d.timestamp).strftime('%d/%m/%Y %H:%M') for d in data],
        'wind_direction_data': [wind_direction_map.get(d.wind_direction, d.wind_direction) for d in data],
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'hora_inicio': hora_inicio,
        'hora_fim': hora_fim,
    }

    return render(request, 'station/wind_direction_chart.html', context)

# Precipitação chart view
def rainfall_chart_view(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fim = request.GET.get('hora_fim')

    if data_inicio and data_fim and hora_inicio and hora_fim:
        try:
            start_datetime = timezone.datetime.fromisoformat(f"{data_inicio} {hora_inicio}")
            end_datetime = timezone.datetime.fromisoformat(f"{data_fim} {hora_fim}")

            # Converte de UTC para o horário local do Django
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)

            # Filtra os dados no banco de dados
            data = WeatherData.objects.filter(
                timestamp__range=[start_datetime, end_datetime],
                rainfall__isnull=False
            ).order_by('timestamp')
        except ValueError:
            return HttpResponseBadRequest("Data ou hora em formato inválido.")
    else:
        # Pega os últimos 20 registros por padrão
        data = WeatherData.objects.filter(
            rainfall__isnull=False
        ).order_by('-timestamp')[:20]
        # Inverte para exibir em ordem cronológica
        data = list(reversed(data))

    context = {
        'labels': [timezone.localtime(d.timestamp).strftime('%d/%m/%Y %H:%M') for d in data],
        'rainfall_data': [d.rainfall for d in data],
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'hora_inicio': hora_inicio,
        'hora_fim': hora_fim,
    }

    return render(request, 'station/rainfall_chart.html', context)

# View que compara DHT e BMP temperatura
def temperature_comparison_chart_view(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fim = request.GET.get('hora_fim')

    if data_inicio and data_fim and hora_inicio and hora_fim:
        try:
            start_datetime = timezone.datetime.fromisoformat(f"{data_inicio} {hora_inicio}")
            end_datetime = timezone.datetime.fromisoformat(f"{data_fim} {hora_fim}")

            # Converte de UTC para o horário local do Django
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)

            # Filtra os dados no banco de dados
            data = WeatherData.objects.filter(
                timestamp__range=[start_datetime, end_datetime],
                dht_temperature__isnull=False,
                bmp_temperature__isnull=False
            ).order_by('timestamp')
        except ValueError:
            return HttpResponseBadRequest("Data ou hora em formato inválido.")
    else:
        # Pega os últimos 20 registros por padrão
        data = WeatherData.objects.filter(
            dht_temperature__isnull=False,
            bmp_temperature__isnull=False
        ).order_by('-timestamp')[:20]
        # Inverte para exibir em ordem cronológica
        data = list(reversed(data))

    context = {
        'labels': [timezone.localtime(d.timestamp).strftime('%d/%m/%Y %H:%M') for d in data],
        'dht_temperature_data': [d.dht_temperature for d in data],
        'bmp_temperature_data': [d.bmp_temperature for d in data],
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'hora_inicio': hora_inicio,
        'hora_fim': hora_fim,
    }

    return render(request, 'station/temperature_comparison_chart.html', context)