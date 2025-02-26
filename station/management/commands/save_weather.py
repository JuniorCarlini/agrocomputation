import os
import json
import django
import requests
from dotenv import load_dotenv
from datetime import timedelta
from django.utils import timezone
from station.models import WeatherSummary
from django.core.management.base import BaseCommand

# Load environment variables from .env file
load_dotenv()

class Command(BaseCommand):
    help = 'Salva previsão do tempo diariamente'

    def handle(self, *args, **kwargs):
        def save_daily_weather():
            # Pega a data de amanhã
            hoje = timezone.now().date()
            amanha = hoje + timedelta(days=1)
            
            # Verifica se já existe registro para amanhã
            if not WeatherSummary.objects.filter(created_at__date=amanha).exists():
                forecast_data = get_weather_forecast()
                
                # Imprimir a estrutura completa dos dados
                print("Tipo de dados recebidos:", type(forecast_data))
                print("Chaves ou conteúdo dos dados:")
                print(json.dumps(forecast_data, indent=2))
                
                if forecast_data:
                    try:
                        # Se for um dicionário com 'timelines', acessar 'daily'
                        if isinstance(forecast_data, dict) and 'timelines' in forecast_data:
                            daily_data = forecast_data['timelines'].get('daily', [])
                        else:
                            daily_data = forecast_data
                        
                        # Encontrar o registro para amanhã
                        target_forecast = None
                        for item in daily_data:
                            # Verificar a estrutura do item
                            print("\nEstrutura de um item:")
                            print(json.dumps(item, indent=2))
                            
                            # Converter a data do item para datetime
                            if isinstance(item, dict) and 'time' in item:
                                item_date = timezone.datetime.fromisoformat(item['time'].replace('Z', '+00:00')).date()
                                if item_date == amanha:
                                    target_forecast = item
                                    break
                        
                        if target_forecast:
                            values = target_forecast.get('values', {})
                            
                            # Criar o registro
                            weather_summary = WeatherSummary(
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
                            
                            weather_summary.save()
                            print(f"Previsão salva para {amanha}")
                            
                            # Debug: imprimir valores salvos
                            print("\nValores salvos:")
                            print(f"Temperatura média: {values.get('temperatureAvg', 0)}")
                            print(f"Temperatura mínima: {values.get('temperatureMin', 0)}")
                            print(f"Temperatura máxima: {values.get('temperatureMax', 0)}")
                            print(f"Umidade média: {values.get('humidityAvg', 0)}")
                            print(f"Velocidade do vento média: {values.get('windSpeedAvg', 0)}")
                            print(f"Probabilidade de chuva média: {values.get('precipitationProbabilityAvg', 0)}")
                            print(f"Acumulação de chuva: {values.get('rainAccumulationSum', 0)}")
                        
                        else:
                            print(f"Nenhum registro encontrado para {amanha}")
                    
                    except Exception as e:
                        print(f"Erro ao processar dados: {e}")
                else:
                    print("Falha ao obter previsão")
            else:
                print(f"Já existe registro para {amanha}")

        def get_weather_forecast():
            # Retrieve API key from environment variable
            api_key = os.getenv('TOMORROW_IO_API_KEY')
            
            if not api_key:
                print("Erro: Chave de API não configurada")
                return None
            
            url = "https://api.tomorrow.io/v4/weather/forecast"
            params = {
                "location": "-11.9043,-62.7174",
                "apikey": api_key
            }
            
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Erro na requisição: {e}")
                return None

        # Rodar imediatamente
        save_daily_weather()

if __name__ == "__main__":
    # Configuração do Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seu_projeto.settings')
    django.setup()
    
    save_daily_weather()