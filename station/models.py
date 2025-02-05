from django.db import models
from django.utils import timezone

class WeatherData(models.Model):
    WIND_DIRECTIONS = [
        ('N', 'North'),
        ('NE', 'Northeast'),
        ('E', 'East'),
        ('SE', 'Southeast'),
        ('S', 'South'),
        ('SW', 'Southwest'),
        ('W', 'West'),
        ('NW', 'Northwest'),
    ]

    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    dht_temperature = models.FloatField(verbose_name='DHT Temperature (°C)', null=True, blank=True)
    bmp_temperature = models.FloatField(verbose_name='BMP Temperature (°C)', null=True, blank=True)
    pressure = models.FloatField(verbose_name='Pressure (hPa)', null=True, blank=True)
    humidity = models.FloatField(verbose_name='Humidity (%)', null=True, blank=True)
    wind_direction = models.CharField(max_length=2, choices=WIND_DIRECTIONS, verbose_name='Wind Direction',null=True ,blank=True)
    wind_speed = models.FloatField(verbose_name='Wind Speed (m/s)', null=True, blank=True)
    rainfall = models.FloatField(verbose_name='Rainfall (mm)', null=True, blank=True)

    class Meta:
        verbose_name = 'Weather Data'
        verbose_name_plural = 'Weather Data'
        ordering = ['-timestamp']

    def __str__(self):
        return f'Record at {self.timestamp.strftime("%Y-%m-%d %H:%M")} - Wind: {self.wind_direction}'
