# Agrocomputação

## Descrição
Este projeto integra duas aplicações Django: uma Estação Meteorológica e um Sistema de Horta Automatizado. Ambos os sistemas utilizam microcontroladores ESP32 para coleta e transmissão periódica de dados.

## Funcionalidades

### Aplicativo da Estação Meteorológica
- Coleta de dados meteorológicos em tempo real
- Monitoramento de temperatura
- Acompanhamento de umidade
- Medição de pressão atmosférica
- Registro de dados com marcação temporal
- Transmissão automatizada de dados via ESP32

### Sistema de Horta Automatizado
- Monitoramento de umidade do solo
- Controle de irrigação
- Acompanhamento de exposição à luz
- Métricas de crescimento das plantas
- Programação automática de rega
- Coleta de dados baseada em ESP32

## Stack Técnica
- Django (Framework Backend)
- ESP32 (Controladores de Hardware)
- Banco de Dados: SQLite/PostgreSQL
- Python para processamento de dados
- APIs RESTful para comunicação de dados

## Instalação
1. Clone o repositório
2. Instale as dependências: `pip install -r requirements.txt`
3. Execute as migrações: `python manage.py migrate`
4. Inicie o servidor: `python manage.py runserver`

## Configuração do ESP32
- Carregue o firmware correspondente em cada ESP32
- Configure as credenciais WiFi
- Defina os intervalos de transmissão de dados
- Verifique as conexões dos sensores

## Contribuição
Sinta-se à vontade para enviar issues e pull requests.

## Licença
Licença MIT
