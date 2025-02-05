from .models import WeatherData
from rest_framework import serializers

class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = [
            'timestamp',
            'dht_temperature',
            'bmp_temperature',
            'pressure',
            'humidity',
            'wind_direction',
            'wind_speed',
            'rainfall'
        ]