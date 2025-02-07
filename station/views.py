from .models import WeatherData
from rest_framework import status
from django.shortcuts import render
from rest_framework.response import Response
from project.decorators import token_required
from .serializers import WeatherDataSerializer
from rest_framework.decorators import api_view

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
    return render(request, 'station/dashboard.html')