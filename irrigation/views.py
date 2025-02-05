from rest_framework import status
from rest_framework.response import Response
from project.decorators import token_required
from rest_framework.decorators import api_view
from .models import StatusFertil, TimeFerti
from .serializers import (DataCollectionSerializer, SolenoidStateSerializer, StoricFertilSerializer, FertilizationStateSerializer)

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