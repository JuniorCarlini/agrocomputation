import json
from rest_framework import status
from django.utils import timezone
from django.shortcuts import render
from rest_framework.response import Response
from project.decorators import token_required
from rest_framework.decorators import api_view
from .serializers import (DataCollectionSerializer, SolenoidStateSerializer, StoricFertilSerializer, FertilizationStateSerializer)
from irrigation.models import (DataCollection, WaterUsage, StatusFertil, StoricFertil, ConfigFertil, FlowRate, SolenoidState, TimeFerti)

@api_view(['POST'])
@token_required
def collect_environmental_data(request):
    serializer = DataCollectionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Environmental data recorded successfully"
        }, status=status.HTTP_201_CREATED)
    return Response({
        "error": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@token_required
def collect_solenoid_state(request):
    serializer = SolenoidStateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Solenoid state recorded successfully"
        }, status=status.HTTP_201_CREATED)
    return Response({
        "error": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@token_required
def collect_historico_fertil(request):
    serializer = StoricFertilSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Irrigation history recorded successfully"
        }, status=status.HTTP_201_CREATED)
    return Response({
        "error": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@token_required
def get_data_fertil_state(request):
    status_fertil = StatusFertil.objects.first()
    if not status_fertil:
        return Response({
            "error": "Fertilization status not found"
        }, status=status.HTTP_404_NOT_FOUND)

    status_fertil.update_status()  # Corrigido para update_status
    time_ferti = TimeFerti.objects.first()
    
    if not time_ferti:
        return Response({
            "error": "Time configuration not found"
        }, status=status.HTTP_404_NOT_FOUND)

    combined_data = {
        'time_ferti_ms': time_ferti.duration_ms,  # Usando duration_ms
        'start_fertil': status_fertil.is_active   # Usando is_active
    }
    
    return Response(combined_data, status=status.HTTP_200_OK)

# Dashboard view
def dashboard_irrigation_view(request):
   hora_atual = timezone.now().hour
   imagem = 'icons/sol.png' if 10 <= hora_atual < 22 else 'icons/lua.png'
   
   try:
       latest_data = DataCollection.objects.latest('timestamp')
       sensor_data = {
           'temperature': float(round(latest_data.temperature, 2)),
           'air_humidity': float(round(latest_data.air_humidity, 2)), 
           'soil_humidity': float(round(latest_data.soil_humidity, 2)),
           'timestamp': timezone.localtime(latest_data.timestamp).strftime('%H:%M')
       }
   except DataCollection.DoesNotExist:
       sensor_data = {
           'temperature': 0.0,
           'air_humidity': 0.0,
           'soil_humidity': 0.0,
           'timestamp': '--:--'
       }

   try:
       status_fertil = StatusFertil.objects.first()
       if status_fertil:
           status_fertil.update_status()
       fertilization_status = {
           'is_active': status_fertil.is_active if status_fertil else False,
           'last_updated': timezone.localtime(status_fertil.last_updated).strftime('%d/%m %H:%M') if status_fertil else '--/-- --:--'
       }
   except StatusFertil.DoesNotExist:
       fertilization_status = {
           'is_active': False,
           'last_updated': '--/-- --:--'
       }

   water_usages = WaterUsage.objects.order_by('-timestamp')[:10]
   water_data = {
       'labels': [timezone.localtime(usage.timestamp).strftime('%H:%M') for usage in water_usages],
       'water_used': [round(usage.water_used, 2) for usage in water_usages],
   }

   try:
       last_irrigation = StoricFertil.objects.latest('timestamp')
       last_irrigation_data = {
           'timestamp': timezone.localtime(last_irrigation.timestamp).strftime('%d/%m %H:%M')
       }
   except StoricFertil.DoesNotExist:
       last_irrigation_data = {
           'timestamp': '--/-- --:--'
       }

   try:
       current_flow = FlowRate.objects.latest('timestamp')
       flow_data = {
           'rate': round(current_flow.rate, 2),
           'timestamp': timezone.localtime(current_flow.timestamp).strftime('%H:%M')
       }
   except FlowRate.DoesNotExist:
       flow_data = {
           'rate': 0.0,
           'timestamp': '--:--'
       }

   try:
       solenoid_status = SolenoidState.objects.latest('timestamp')
       solenoid_data = {
           'is_open': solenoid_status.is_open,
           'timestamp': timezone.localtime(solenoid_status.timestamp).strftime('%H:%M')
       }
   except SolenoidState.DoesNotExist:
       solenoid_data = {
           'is_open': False,
           'timestamp': '--:--'
       }

   try:
       config_fertil = ConfigFertil.objects.first()
       config_data = {
           'duration_hours': config_fertil.duration_hours if config_fertil else 1
       }
   except ConfigFertil.DoesNotExist:
       config_data = {
           'duration_hours': 1
       }

   context = {
       'imagem': imagem,
       'sensor_data': json.dumps(sensor_data),
       'fertilization_status': json.dumps(fertilization_status),
       'water_data': json.dumps(water_data),
       'last_irrigation': json.dumps(last_irrigation_data),
       'flow_data': json.dumps(flow_data),
       'solenoid_data': json.dumps(solenoid_data),
       'config_data': json.dumps(config_data)
   }
   
   return render(request, 'irrigation/dashboard.html', context)

# Chart views
def temperature_chart_view(request):
    # Obtem os dados da URL, se disponíveis
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fim = request.GET.get('hora_fim')

    # Verifica se todos os filtros de data/hora foram fornecidos
    if data_inicio and data_fim and hora_inicio and hora_fim:
        try:
            # Combina data e hora em um único timestamp
            start_datetime = timezone.datetime.fromisoformat(f"{data_inicio} {hora_inicio}")
            end_datetime = timezone.datetime.fromisoformat(f"{data_fim} {hora_fim}")

            # Converte de UTC para o horário local do navegador
            # Usando o timezone local do Django
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)

            # Filtra os dados no banco de dados
            data = DataCollection.objects.filter(timestamp__range=[start_datetime, end_datetime]).order_by('timestamp')
        except ValueError:
            return HttpResponseBadRequest("Data ou hora em formato inválido.")
    else:
        # Pega os últimos 20 registros por padrão
        data = DataCollection.objects.all().order_by('-timestamp')[:20]

    # Converte os timestamps para o horário local antes de exibi-los
    context = {
        'labels': [timezone.localtime(d.timestamp).strftime('%d-%m-%Y %H:%M') for d in data],
        'temperature_data': [d.temperature for d in data],
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'hora_inicio': hora_inicio,
        'hora_fim': hora_fim,
    }
    return render(request, 'irrigation/temperature_chart.html', context)

def air_humidity_chart_view(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fim = request.GET.get('hora_fim')

    if data_inicio and data_fim and hora_inicio and hora_fim:
        try:
            start_datetime = timezone.datetime.fromisoformat(f"{data_inicio} {hora_inicio}")
            end_datetime = timezone.datetime.fromisoformat(f"{data_fim} {hora_fim}")

            # Converte de UTC para o horário local do navegador
            # Usando o timezone local do Django
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)

            # Filtra os dados no banco de dados
            data = DataCollection.objects.filter(timestamp__range=[start_datetime, end_datetime]).order_by('timestamp')
        except ValueError:
            return HttpResponseBadRequest("Data ou hora em formato inválido.")
    else:
        # Pega os últimos 20 registros por padrão
        data = DataCollection.objects.all().order_by('-timestamp')[:20]

    context = {
        'labels': [timezone.localtime(d.timestamp).strftime('%d-%m-%Y %H:%M') for d in data],
        'air_humidity_data': [d.air_humidity for d in data],
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'hora_inicio': hora_inicio,
        'hora_fim': hora_fim,
    }

    return render(request, 'irrigation/air_humidity_chart.html', context)

def soil_humidity_chart_view(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fim = request.GET.get('hora_fim')

    if data_inicio and data_fim and hora_inicio and hora_fim:
        try:
            start_datetime = timezone.datetime.fromisoformat(f"{data_inicio} {hora_inicio}")
            end_datetime = timezone.datetime.fromisoformat(f"{data_fim} {hora_fim}")

            # Converte de UTC para o horário local do navegador
            # Usando o timezone local do Django
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)

            # Filtra os dados no banco de dados
            data = DataCollection.objects.filter(timestamp__range=[start_datetime, end_datetime]).order_by('timestamp')
        except ValueError:
            return HttpResponseBadRequest("Data ou hora em formato inválido.")
    else:
        # Pega os últimos 20 registros por padrão
        data = DataCollection.objects.all().order_by('-timestamp')[:20]

    context = {
        'labels': [timezone.localtime(d.timestamp).strftime('%d-%m-%Y %H:%M') for d in data],
        'soil_humidity_data': [d.soil_humidity for d in data],
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'hora_inicio': hora_inicio,
        'hora_fim': hora_fim,
    }

    return render(request, 'irrigation/soil_humidity_chart.html', context)

def water_usage_chart_view(request):
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
            water_usages = WaterUsage.objects.filter(timestamp__range=[start_datetime, end_datetime]).order_by('timestamp')
        except ValueError:
            return HttpResponseBadRequest("Data ou hora em formato inválido.")
    else:
        # Pega os últimos 20 registros por padrão
        water_usages = WaterUsage.objects.all().order_by('-timestamp')[:20]

    # Extraindo dados
    water_usage_data = [round(usage.water_used, 2) for usage in water_usages]
    labels = [timezone.localtime(usage.timestamp).strftime('%d-%m-%Y %H:%M') for usage in water_usages]

    context = {
        'water_usage_data': water_usage_data,
        'labels': labels,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'hora_inicio': hora_inicio,
        'hora_fim': hora_fim,
    }

    return render(request, 'irrigation/use_water_chart.html', context)

def fertil_usage_chart_view(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    hora_inicio = request.GET.get('hora_inicio')
    hora_fim = request.GET.get('hora_fim')

    if data_inicio and data_fim and hora_inicio and hora_fim:
        try:
            start_datetime = timezone.datetime.fromisoformat(f"{data_inicio} {hora_inicio}")
            end_datetime = timezone.datetime.fromisoformat(f"{data_fim} {hora_fim}")
            
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)
            
            fertil_usages = StoricFertil.objects.filter(
                timestamp__range=[start_datetime, end_datetime]
            ).order_by('timestamp')
        except ValueError:
            return HttpResponseBadRequest("Data ou hora em formato inválido.")
    else:
        fertil_usages = StoricFertil.objects.all().order_by('-timestamp')[:20]

    irrigation_data = [1 for _ in fertil_usages]
    labels = [timezone.localtime(usage.timestamp).strftime('%d-%m-%Y %H:%M') for usage in fertil_usages]

    context = {
        'irrigation_data': irrigation_data,
        'labels': labels,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'hora_inicio': hora_inicio,
        'hora_fim': hora_fim,
    }

    return render(request, 'irrigation/uso_fertil_chart.html', context)