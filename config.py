from os import environ
from sys import path
from pathlib import Path

AWS_LAMBDA_FUNCTION_NAME_ENV = 'AWS_LAMBDA_FUNCTION_NAME'
IN_AWS_LAMBDA = AWS_LAMBDA_FUNCTION_NAME_ENV in environ
if IN_AWS_LAMBDA:
    lib_folder = Path(__file__).parent / 'libs_for_aws_lambda'
    path.append(str(lib_folder))

AWS_REGION = environ.get('AWS_REGION', 'us-east-1')

OPENWEATHERMAP_SITE = 'https://api.openweathermap.org'
OPENWEATHERMAP_GEOCODING_PREFIX = f'{OPENWEATHERMAP_SITE}/geo/1.0/direct?limit=1'
OPENWEATHERMAP_GET_WEATHER_PREFIX = f'{OPENWEATHERMAP_SITE}/data/2.5/weather'
OPENWEATHERMAP_GET_WEATHER_FIXED_PARAMS = '&units=metric&lang=ru'


METEOBLUE_GEOCODING_PREFIX = 'https://www.meteoblue.com/ru/server/search/query3?'
METEOBLUE_GEOCODING_FIXED_PARAMS = 'language=ru&itemsPerPage=10&query='
# METEOBLUE_GET_CITI_INFO_PREFIX = 'https://www.meteoblue.com/en/weather/week/'
METEOBLUE_GET_CITI_INFO_PREFIX = 'https://www.meteoblue.com/ru/погода/неделя/'

METEOBLUE_PICTURE_URL_PREFIX = 'https://my.meteoblue.com/visimage/meteogram_web_hd' # '?look='
METEOBLUE_TIMEZONE_PLUS_PREFIX = 'UTC +'
METEOBLUE_TIMEZONE_MINUS_PREFIX = 'UTC -'
METEOBLUE_TIMEZONE_GMT = '<span class="value">GMT </span>'
METEOBLUE_TIMEZONE_WET = '<span class="value">WET </span>'

METEOBLUE_WATER_TEMP_NODE_TITLE = 'title="Tемпература воды'
METEOBLUE_WATER_TEMP_BLOCK_START = '<td><div class="cell">'
METEOBLUE_WATER_TEMP_BLOCK_END = '°</div></td>'

METEOBLUE_SUNRISE_BLOCK_START = 'aria-label="Восход солнца">▲</span> '
METEOBLUE_SUNSET_BLOCK_START = 'aria-label="Закат">▼</span> '

METEOBLUE_COOKIES = {'temp':'CELSIUS', 'locale': 'ru_RU', 'speed': 'METER_PER_SECOND'}

TELEGRAM_URL_PREFIX = 'https://api.telegram.org/bot'

BOT_NAME = 'kobuleti_weather_bot'

DEFAULT_DARKMODE = False
SWITCH_DARKMODE_COMMAND = '/dark'

DEFAULT_CITY = 'Кобулети'
CHAT_CITY_EXPIRATION_TIME_SEC = 60 * 60 * 24 * 30  # 60 * 60 * 24 * 365

LAMBDA_SUCCESS = {'statusCode': 200, 'body': 'Success'}

MAX_SAVED_CITIES_PER_USER = 5