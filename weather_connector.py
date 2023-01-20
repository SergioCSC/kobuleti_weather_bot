import config as cfg
import api_keys
import utils

from typing import NamedTuple
import json


class Weather(NamedTuple):
    city_name: str
    temp_celsius: float
    pressure_mm_hg: int
    humidity_percent: int
    wind_speed_ms: float
    short_description: str
    long_description: str


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
