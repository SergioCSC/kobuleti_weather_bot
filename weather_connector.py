import config as cfg
import api_keys
import utils

from PIL import Image

import io
from typing import NamedTuple
import json
from urllib.request import urlopen


class Weather(NamedTuple):
    city_name: str
    temp_celsius: float
    pressure_mm_hg: int
    humidity_percent: int
    wind_speed_ms: float
    short_description: str
    long_description: str
    
    
    
def create_weather_message(w: Weather) -> str:
    weather_icon = ''
    if w.short_description == 'Clear':
        weather_icon = '🌞 '
    elif w.short_description == 'Clouds':
        weather_icon = '☁ '
    elif w.short_description == 'Rain':
        weather_icon = '💧 '
    elif w.short_description == 'Snow':
        weather_icon = '❄ '
    else: 
        weather_icon = w.short_description

    message = (
        f'🏖 *{w.city_name}*\n'
        f'🌡 {w.temp_celsius:.0f} °C, {weather_icon}{w.long_description}\n'
        f'💨 ветер {w.wind_speed_ms:.0f} м/с\n'
        f'🚰 влажность {w.humidity_percent}%\n'
        f'🎈 давление {w.pressure_mm_hg} мм рт\. ст\.'
    )
    
    return message
  

def get_weather_image() -> io.BytesIO:
    img = Image.open(urlopen(cfg.WEATHER_IMAGE_URL))
    area = (0, 0, 2230, 550)
    cropped_img = img.crop(area)
    
    bytes_object = io.BytesIO()
    cropped_img.save(bytes_object, format='png')
    bytes_object.seek(0)
    return bytes_object


def http_get_weather() -> Weather:
    WEATHER_SITE = f'{cfg.WEATHER_SITE_PREFIX}?{cfg.WEATHER_SITE_PARAMS}' \
            f'&appid={api_keys.OPENWEATHERMAP_ORG_APP_ID}'
    message = utils.get(WEATHER_SITE)
    d = json.load(message)
    temp_celsius = float(d['main']['temp'])  # - 273.15
    pressure_mm_hg = int(float(d['main']['pressure']) * 3 / 4)
    humidity_percent: int = int(d['main']['humidity'])
    wind_speed_ms = float(d['wind']['speed'])
    short_description = d['weather'][0]['main']
    long_description = d['weather'][0]['description']
    
    # weather_icon = d['weather'][0]['icon']
    
    return Weather('Кобулети', 
                   temp_celsius, 
                   pressure_mm_hg, 
                   humidity_percent, 
                   wind_speed_ms, 
                   short_description, 
                   long_description
                  )
