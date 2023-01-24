from os import environ
from sys import path
from pathlib import Path

AWS_LAMBDA_FUNCTION_NAME_ENV = 'AWS_LAMBDA_FUNCTION_NAME'
IN_AWS_LAMBDA = AWS_LAMBDA_FUNCTION_NAME_ENV in environ
if IN_AWS_LAMBDA:
    lib_folder = Path(__file__).parent / 'libs_for_aws_lambda'
    path.append(str(lib_folder))

AWS_REGION = environ.get('AWS_REGION', 'us-east-1')

WEATHER_SITE_PREFIX = 'https://api.openweathermap.org/data/2.5/weather'
WEATHER_SITE_PARAMS = 'lat=41.8141&lon=41.7739&units=metric&lang=ru'

WEATHER_IMAGE_URL = 'https://my.meteoblue.com/visimage/meteogram_web_hd?look=KILOMETER_PER_HOUR%2CCELSIUS%2CMILLIMETER%2Cdarkmode&apikey=5838a18e295d&temperature=C&windspeed=kmh&precipitationamount=mm&winddirection=3char&city=K%27obulet%27i&iso2=ge&lat=41.8214&lon=41.7792&asl=3&tz=Asia%2FTbilisi&lang=en&sig=a4868efb7f837c79aa59b5b95505a0b1'

TELEGRAM_URL_PREFIX = 'https://api.telegram.org/bot'