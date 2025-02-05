from django.db import models
from datetime import timedelta
from django.utils import timezone

class TimeFerti(models.Model):
    duration_ms = models.PositiveIntegerField(default=0, help_text="Pump operation time in milliseconds")

    def __str__(self):
        return f"Pump operation time: {self.duration_ms}ms"

class ConfigFertil(models.Model):
    duration_hours = models.PositiveIntegerField(default=1, help_text="Fertilization duration in hours")

    def __str__(self):
        return f"Fertilization duration: {self.duration_hours}h"

class StoricFertil(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'timestamp'

    def __str__(self):
        return f"Irrigation performed at: {self.timestamp}"

class StatusFertil(models.Model):
    is_active = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    def update_status(self):
        latest_irrigation = StoricFertil.objects.last()
        config = ConfigFertil.objects.first()

        if not latest_irrigation or not config:
            self.is_active = True
        else:
            time_limit = latest_irrigation.timestamp + timedelta(hours=config.duration_hours)
            self.is_active = timezone.now() > time_limit

        self.save()

    def __str__(self):
        return f"Fertilization status: {'Active' if self.is_active else 'Inactive'}"

class FlowRate(models.Model):
    rate = models.FloatField(help_text="Flow rate in L/min")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'timestamp'

    def __str__(self):
        return f"Flow rate: {self.rate} L/min"

class SolenoidState(models.Model):
    is_open = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.is_open:
            last_open = SolenoidState.objects.filter(is_open=True).latest('timestamp')
            if last_open:
                duration = timezone.now() - last_open.timestamp
                flow_rate = FlowRate.objects.latest('timestamp')
                flow_rate_lps = (flow_rate.rate if flow_rate else 30.0) / 60.0
                water_used = flow_rate_lps * duration.total_seconds()
                
                WaterUsage.objects.create(
                    solenoid_state=last_open,
                    water_used=water_used
                )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Solenoid {'open' if self.is_open else 'closed'} at {self.timestamp}"

class WaterUsage(models.Model):
    solenoid_state = models.ForeignKey(SolenoidState, on_delete=models.CASCADE, related_name='water_usages')
    water_used = models.FloatField(help_text="Water usage in liters")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Water used: {self.water_used}L at {self.timestamp}"

class DataCollection(models.Model):
    temperature = models.FloatField(help_text="Temperature in Celsius")
    air_humidity = models.FloatField(help_text="Air humidity in percentage")
    soil_humidity = models.FloatField(help_text="Soil humidity in percentage")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'timestamp'

    def __str__(self):
        return f"T={self.temperature}°C, Air={self.air_humidity}%, Soil={self.soil_humidity}%"

class Configuration(models.Model):
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Configuration token: {self.token}</document_content>"