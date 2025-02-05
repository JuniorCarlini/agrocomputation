from rest_framework import serializers
from .models import DataCollection, SolenoidState, StatusFertil, StoricFertil, TimeFerti

class SolenoidStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolenoidState
        fields = ['is_open']

class DataCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataCollection
        fields = ['temperature', 'air_humidity', 'soil_humidity']

class StoricFertilSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoricFertil
        fields = ['timestamp']

class FertilizationStateSerializer(serializers.Serializer):
    duration_ms = serializers.IntegerField(source='duration_ms')
    is_active = serializers.BooleanField(source='start_fertil')

    def to_representation(self, instance):
        time_ferti = TimeFerti.objects.first()
        status_fertil = StatusFertil.objects.first()

        if not all([time_ferti, status_fertil]):
            return {'duration_ms': None, 'is_active': None}

        return {
            'duration_ms': time_ferti.time_ferti_ms,
            'is_active': status_fertil.start_fertil
        }