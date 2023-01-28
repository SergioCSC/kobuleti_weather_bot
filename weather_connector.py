import config as cfg
import utils
import api_keys
import my_exceptions

from PIL import Image

import re
import io
from typing import NamedTuple
import json
import requests


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
        weather_icon = w.short_description + ' '

    message = (
        f'🏖 *{w.city_name}*\n'
        f'🌡 {w.temp_celsius:.0f} °C, {weather_icon}{w.long_description}\n'
        f'💨 ветер {w.wind_speed_ms:.0f} м/с\n'
        f'🚰 влажность {w.humidity_percent}%\n'
        f'🎈 давление {w.pressure_mm_hg} мм рт. ст.'
    )
    
    return message

def get_meteoblue_params(city_name: str) -> tuple:
    url = cfg.METEOBLUE_GEOCODING_PREFIX + city_name
    cookies = {'locale': 'ru_RU'}
    response = requests.get(url, cookies=cookies)
    message = response.text
    d = json.loads(message)
    
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
    cookies = {'temp':'CELSIUS', 'darkmode': 'false',
               'locale': 'ru_RU', 'speed': 'METER_PER_SECOND'}
    response = requests.get(url, cookies=cookies)
    body = response.text
    
    picture_url_starts = [m.start() for m in re.finditer(cfg.METEOBLUE_PICTURE_URL_PREFIX, body)]
    if len(picture_url_starts) != 1:
        raise my_exceptions.MeteoblueParsingError(
                f'found picture url starts: {picture_url_starts}')
    picture_url_start = picture_url_starts[0]
    picture_url_len = body[picture_url_start:].find(' ')
    picture_url = body[picture_url_start:picture_url_start + picture_url_len]
    picture_url = picture_url.replace('&amp;', '&')
    return picture_url


def get_picture_url(city_name: str) -> str:
    city, iso2, lat, lon, asl, tz, url_suffix_for_sig \
            = get_meteoblue_params(city_name)
    
    
    # iso2 = iso2.lower()
    # city = urllib.parse.quote(city.encode('utf-8'), safe='') 
    # tz = urllib.parse.quote(tz.encode('utf-8'), safe='') 
    
    # url = f'&city={city}&iso2={iso2}&lat={lat}&lon={lon}&asl={asl}&tz={tz}'
    
    picure_url = get_meteoblue_pic_url(url_suffix_for_sig)
    
    return picure_url


def get_weather_image(city_name: str) -> io.BytesIO:
    # utils.print_with_time(f'    START getting picture url')
    picture_url = get_picture_url(city_name)
    utils.print_with_time(f'    got picture url')
    # utils.print_with_time(f'    START getting picture')
    response = requests.get(picture_url)
    utils.print_with_time(f'    got picture')
    # utils.print_with_time(f'    START cropping picture')
    img = Image.open(io.BytesIO(response.content))
    h_1 = 600
    h_2 = h_1 + (img.height - h_1) // 2
    h_3 = h_2 + (img.height - h_1) // 2
    area_1 = (0, 0, img.width, h_1)
    area_2 = (0, h_1, img.width, h_2)
    area_3 = (0, h_2, img.width, h_3)
    cropped_3 = img.crop(area_3)
    img.paste(cropped_3, area_2)
    result = img.crop((0, 0, img.width, h_2))
    
    bytes_object = io.BytesIO()
    result.save(bytes_object, format='png')
    bytes_object.seek(0)
    utils.print_with_time(f'    cropped picture')
    return bytes_object


def get_openweathermap_coordinates_and_name(city_name: str) -> tuple[str, str]:
    url = f'{cfg.OPENWEATHERMAP_GEOCODING_PREFIX}' \
            f'&q={city_name}' \
            f'&appid={api_keys.OPENWEATHERMAP_ORG_APP_ID}'

    response = requests.get(url)
    message = response.text
    d = json.loads(message)[0]
    
    city_ru_name = d.get('local_names', {}).get('ru', city_name)
    lat = d['lat']
    lon = d['lon']
    coordinates = f'lat={lat}&lon={lon}'
    return coordinates, city_ru_name


def http_get_weather(city_name: str) -> Weather:
    coordinates, city_ru_name = get_openweathermap_coordinates_and_name(city_name)
    weather_url = f'{cfg.OPENWEATHERMAP_GET_WEATHER_PREFIX}' \
            f'?{cfg.OPENWEATHERMAP_GET_WEATHER_FIXED_PARAMS}' \
            f'&{coordinates}' \
            f'&appid={api_keys.OPENWEATHERMAP_ORG_APP_ID}'
    response = requests.get(weather_url)
    message = response.text
    d = json.loads(message)
    temp_celsius = float(d['main']['temp'])  # - 273.15
    pressure_mm_hg = int(float(d['main']['pressure']) * 3 / 4)
    humidity_percent: int = int(d['main']['humidity'])
    wind_speed_ms = float(d['wind']['speed'])
    short_description = d['weather'][0]['main']
    long_description = d['weather'][0]['description']
    
    # weather_icon = d['weather'][0]['icon']
    
    return Weather(city_ru_name, 
                   temp_celsius, 
                   pressure_mm_hg, 
                   humidity_percent, 
                   wind_speed_ms, 
                   short_description, 
                   long_description
                  )
