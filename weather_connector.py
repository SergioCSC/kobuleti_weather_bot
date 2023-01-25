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

def get_meteoblue_params(city_name: str) -> tuple:
    url = cfg.METEOBLUE_GEOCODING_PREFIX + city_name
    message = utils.get(url)
    d = json.load(message)
    
    citi_info = d['results'][0]
    
    city = citi_info['name']
    iso2 = citi_info['iso2']
    lat = citi_info['lat']
    lon = citi_info['lon']
    asl = citi_info['asl']
    tz = citi_info['timezone']
    url_suffix_for_sig = citi_info['url']
    return city, iso2, lat, lon, asl, tz, url_suffix_for_sig


def get_meteoblue_pic_url(url_suffix_for_sig) -> str:
    url = cfg.METEOBLUE_GET_CITI_INFO_PREFIX + url_suffix_for_sig
    body = str(utils.get(url).read())
    picture_url_start = body.find(cfg.METEOBLUE_PICTURE_URL_PREFIX)
    picture_url_len = body[picture_url_start:].find(' ')
    picture_url = body[picture_url_start:picture_url_start + picture_url_len]
    picture_url = picture_url.replace('&amp;', '&')
    return picture_url


def get_picture_url_from_meteoblue_params(city_name: str) -> str:
    url = cfg.METEOBLUE_GEOCODING_PREFIX + city_name
    city, iso2, lat, lon, asl, tz, url_suffix_for_sig \
            = get_meteoblue_params(city_name)
    
    
    # iso2 = iso2.lower()
    # city = urllib.parse.quote(city.encode('utf-8'), safe='') 
    # tz = urllib.parse.quote(tz.encode('utf-8'), safe='') 
    
    # url = f'&city={city}&iso2={iso2}&lat={lat}&lon={lon}&asl={asl}&tz={tz}'
    
    picure_url = get_meteoblue_pic_url(url_suffix_for_sig)
    
    return picure_url


def get_weather_image(city_name: str) -> io.BytesIO:
    picture_url = get_picture_url_from_meteoblue_params(city_name)
    img = Image.open(urlopen(picture_url))
    area = (0, 0, 2230, 550)
    cropped_img = img.crop(area)
    
    bytes_object = io.BytesIO()
    cropped_img.save(bytes_object, format='png')
    bytes_object.seek(0)
    return bytes_object


def get_openweathermap_coordinates(city_name: str) -> str:
    return 'lat=41.8141&lon=41.7739'  # TODO


def http_get_weather(city_name: str) -> Weather:
    coordinates = get_openweathermap_coordinates(city_name)
    WEATHER_SITE = f'{cfg.WEATHER_SITE_PREFIX}' \
            f'?{cfg.WEATHER_SITE_FIXED_PARAMS}' \
            f'&{coordinates}' \
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
    
    return Weather(city_name, 
                   temp_celsius, 
                   pressure_mm_hg, 
                   humidity_percent, 
                   wind_speed_ms, 
                   short_description, 
                   long_description
                  )
