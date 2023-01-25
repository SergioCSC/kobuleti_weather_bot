from os import environ
from sys import path
from pathlib import Path

AWS_LAMBDA_FUNCTION_NAME_ENV = 'AWS_LAMBDA_FUNCTION_NAME'
IN_AWS_LAMBDA = AWS_LAMBDA_FUNCTION_NAME_ENV in environ
if IN_AWS_LAMBDA:
    lib_folder = Path(__file__).parent / 'libs_for_aws_lambda'
    path.append(str(lib_folder))

AWS_REGION = environ.get('AWS_REGION', 'us-east-1')

OPENWEATHERMAP_GEOCODING_PREFIX = 'http://api.openweathermap.org/geo/1.0/direct?limit=1'
OPENWEATHERMAP_SITE_PREFIX = 'https://api.openweathermap.org/data/2.5/weather'
OPENWEATHERMAP_SITE_FIXED_PARAMS = '&units=metric&lang=ru'


METEOBLUE_GEOCODING_PREFIX = 'https://www.meteoblue.com/en/server/search/query3?itemsPerPage=1&query='
METEOBLUE_GET_CITI_INFO_PREFIX = 'https://www.meteoblue.com/en/weather/week/'

METEOBLUE_PICTURE_URL_PREFIX = 'https://my.meteoblue.com/visimage/meteogram_web_hd?look=KILOMETER_PER_HOUR'
METEOBLUE_GET_IMAGE_PREFIX = 'https://my.meteoblue.com/visimage/meteogram_web_hd?look=KILOMETER_PER_HOUR%2CCELSIUS%2CMILLIMETER%2Cdarkmode&apikey=5838a18e295d&temperature=C&windspeed=kmh&precipitationamount=mm&winddirection=3char'
METEOBLUE_GET_IMAGE_POSTFIX = '&lang=en&sig='
METEOBLUE_GET_IMAGE_FIXED_PARAMS = '&city=K%27obulet%27i&iso2=ge&lat=41.8214&lon=41.7792&asl=3&tz=Asia%2FTbilisi'

TELEGRAM_URL_PREFIX = 'https://api.telegram.org/bot'