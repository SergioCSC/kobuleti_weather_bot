from os import environ

AWS_LAMBDA_FUNCTION_NAME_ENV = 'AWS_LAMBDA_FUNCTION_NAME'
IN_AWS_LAMBDA = AWS_LAMBDA_FUNCTION_NAME_ENV in environ
AWS_REGION = environ.get('AWS_REGION', 'us-east-1')

WEATHER_SITE_PREFIX = 'https://api.openweathermap.org/data/2.5/weather'
WEATHER_SITE_PARAMS = 'lat=41.8141&lon=41.7739&units=metric&lang=ru'
TELEGRAM_URL_PREFIX = 'https://api.telegram.org/bot'