from django.db import models
from django.utils import timezone

class WeatherData(models.Model):
    WIND_DIRECTIONS = [
        ('N', 'Norte'),
        ('L', 'Leste'),
        ('S', 'Sul'),
        ('O', 'Oeste'),
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

class WeatherSummary(models.Model):
   # Temperatura
   temperature_current = models.FloatField()
   temperature_min = models.FloatField()
   temperature_max = models.FloatField()

   # Umidade
   humidity_current = models.FloatField()
   humidity_min = models.FloatField()
   humidity_max = models.FloatField()

   # Vento
   wind_speed = models.FloatField()
   wind_gust_speed = models.FloatField()

   # Chuva
   rain_probability = models.FloatField()
   rain_accumulation = models.FloatField()

   # Timestamp de criação
   created_at = models.DateTimeField(auto_now_add=True)

   @classmethod
   def create_from_forecast_data(cls, forecast_data):
       """
       Método de classe para criar uma instância a partir dos dados da API
       """
       values = forecast_data.get('values', {})

       return cls(
           temperature_current=values.get('temperatureAvg', 0),
           temperature_min=values.get('temperatureMin', 0),
           temperature_max=values.get('temperatureMax', 0),
           
           humidity_current=values.get('humidityAvg', 0),
           humidity_min=values.get('humidityMin', 0),
           humidity_max=values.get('humidityMax', 0),
           
           wind_speed=values.get('windSpeedAvg', 0),
           wind_gust_speed=values.get('windGustMax', 0),
           
           rain_probability=values.get('precipitationProbabilityAvg', 0),
           rain_accumulation=values.get('rainAccumulationSum', 0)
       )

   def __str__(self):
       return f"Weather Summary - {self.created_at}"

   class Meta:
       verbose_name = "Weather Summary"
       verbose_name_plural = "Weather Summaries"
       ordering = ['-created_at']
