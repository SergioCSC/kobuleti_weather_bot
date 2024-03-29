import config as cfg
import utils
import api_keys
import my_exceptions
from messages import NOT_FOUND_WEATHER_TEXTS
from city import City
from time_of_day import TimeOfDay, parse_time

from PIL import Image

import re
import io
import json
import requests
import traceback
from typing import NamedTuple
from typing import Optional
from typing import Generator


class Weather(NamedTuple):
    city_name: str
    lat: float
    lon: float
    temp_celsius: float
    pressure_mm_hg: int
    humidity_percent: int
    wind_speed_ms: float
    short_description: str
    long_description: str


def get_weather_text(city: City, water_temp: Optional[int], 
                     sunrise: Optional[TimeOfDay], 
                     sunset: Optional[TimeOfDay]) -> str:
    try:
        # utils.print_with_time(f'START got text from openweathermap.org')
        weather = _http_get_weather(city)
        text = _create_weather_text(city, weather, water_temp, sunrise, sunset)
        utils.print_with_time(f'got text from openweathermap.org')
        return text
    except Exception as e:
        utils.print_with_time(f'Exception {e} in weather_connector.http_get_weather({city.local_name})')
        utils.print_with_time(f'Traceback:\n{traceback.print_exc}')
        return ''


def get_weather_image_tz_temp_sun(city: City, dark_mode: bool) \
        -> tuple[Optional[io.BytesIO], str, Optional[int], 
                 Optional[TimeOfDay], Optional[TimeOfDay]]:
    try:
        return _get_weather_image_tz_temp_sun(city, dark_mode)
    except Exception as e:
        utils.print_with_time(f'Exception {e} in'
                f' weather_connector.get_weather_image({city.local_name})')
        utils.print_with_time(f'Traceback:\n{traceback.print_exc}')
        return None, '', None, None, None


def _http_get_weather(city: City) -> Weather:
    coordinates = f'lat={city.lat}&lon={city.lon}'
    
    weather_url = f'{cfg.OPENWEATHERMAP_GET_WEATHER_PREFIX}' \
            f'?{cfg.OPENWEATHERMAP_GET_WEATHER_FIXED_PARAMS}' \
            f'&{coordinates}' \
            f'&appid={api_keys.OPENWEATHERMAP_ORG_APP_ID}'
    response = requests.get(weather_url)
    message = response.text
    
    d = json.loads(message)
    
    owm_name = d['name']
    owm_lat = d['coord']['lat']
    owm_lon = d['coord']['lon']
    
    temp_celsius = float(d['main']['temp'])  # - 273.15
    pressure_mm_hg = int(float(d['main']['pressure']) * 3 / 4)
    humidity_percent: int = int(d['main']['humidity'])
    wind_speed_ms = float(d['wind']['speed'])
    short_description = d['weather'][0]['main']
    long_description = d['weather'][0]['description']
    
    weather_icon = d['weather'][0]['icon']
    
    return Weather(city.local_name,  # owm_name, 
                   owm_lat,
                   owm_lon,
                   temp_celsius, 
                   pressure_mm_hg, 
                   humidity_percent, 
                   wind_speed_ms, 
                   short_description, 
                   long_description
                  )

    
def _create_weather_text(city: City, w: Weather, 
                         water_temp: Optional[int],
                         sunrise: Optional[TimeOfDay], 
                         sunset: Optional[TimeOfDay]) -> str:
    weather_icon = ''
    if w.short_description == 'Clear':
        weather_icon = '🌞 '
    elif w.short_description == 'Clouds':
        weather_icon = '☁ '
    elif w.short_description == 'Rain':
        weather_icon = '💧 '
    elif w.short_description == 'Drizzle':
        weather_icon = '🌧 '
    elif w.short_description == 'Mist':
        weather_icon = '🌫 '
    elif w.short_description == 'Smoke':
        weather_icon = '🌫 '
    elif w.short_description == 'Snow':
        weather_icon = '❄ '
    elif w.short_description == 'Thunderstorm':
        weather_icon = '⚡ '
    else: 
        weather_icon = w.short_description + ' '

    if w.long_description == 'облачно с прояснениями':
        weather_icon = '⛅ '

    # country = city.country if city.country != 'Россия' else 'РФ'

    city_text = \
            f'🏘 *{w.city_name}*' \
            f' _{city.admin_subject},' \
            f' {city.country}' \
            f'_'
            # f' {city.population:,} чел,' \
            # f' {city.asl}м н.у.м.' \
            # f' {w.lat:.3f},'\
            # f' {w.lon:.3f}'\
    
    sunrise_total_minutes = sunrise.hours * 60 + sunrise.minutes
    sunset_total_minutes = sunset.hours * 60 + sunset.minutes
    zenith_total_minutes = sunrise_total_minutes + (sunset_total_minutes - sunrise_total_minutes) // 2
    zenith = TimeOfDay(zenith_total_minutes // 60, zenith_total_minutes % 60)
    
    if water_temp is not None:
        water_text = f' ,  🌊 вода {water_temp} °C'
    else:
        water_text = f''
    
    weather_text = (
        f'🌡 {w.temp_celsius:.0f} °C{water_text}'
        f'\n{weather_icon}{w.long_description}'
        f'\n💨 ветер {w.wind_speed_ms:.0f} м/с'
        f'\n🚰 влажность {w.humidity_percent}%'
        f'\n🎈 давление {w.pressure_mm_hg} мм рт. ст.'
        f'\n🌅 восход {sunrise.hours}:{sunrise.minutes:02}'
        f'\n☀ зенит {zenith.hours}:{zenith.minutes:02}'
        f'\n🌇 закат {sunset.hours}:{sunset.minutes:02}'
    )

    return city_text + '\n\n' + weather_text


def get_city_options(
        city_name: Optional[str]=None, 
        lat: Optional[float]=None, 
        lon: Optional[float]=None) \
        -> Generator[tuple, None, None]:
    
    if city_name:
        url = cfg.METEOBLUE_GEOCODING_PREFIX \
                + cfg.METEOBLUE_GEOCODING_FIXED_PARAMS \
                + city_name
    else:
        url = cfg.METEOBLUE_GEOCODING_PREFIX \
                + cfg.METEOBLUE_GEOCODING_FIXED_PARAMS \
                + f'{lat} {lon}'

    cookies = cfg.METEOBLUE_COOKIES
    response = requests.get(url, cookies=cookies)
    message = response.text
    d = json.loads(message)
    
    for citi_info in d['results']:
    
        local_name = citi_info['name']
        iso2 = citi_info['iso2']
        country = citi_info['country']
        admin_subject = citi_info['admin1']
        lat = citi_info['lat']
        lon = citi_info['lon']
        asl = citi_info['asl']
        population = citi_info['population']
        distance = citi_info['distance']
        tz = citi_info['timezone']
        url_suffix_for_sig = citi_info['url']
        
        city = City(local_name, iso2, country, admin_subject, lat, lon, asl,
                    population, distance, tz, url_suffix_for_sig)
        yield city


def _get_meteoblue_pic_url(body: str) -> str:
    picture_url_starts = [m.start() for m in re.finditer(cfg.METEOBLUE_PICTURE_URL_PREFIX, body)]
    if len(picture_url_starts) != 1:
        starts = [body[i:i + 100] for i in picture_url_starts]
        raise my_exceptions.MeteoblueParsingError(
                f'found picture url starts: {starts}')
    picture_url_start = picture_url_starts[0]
    picture_url_len = body[picture_url_start:].find(' ')
    picture_url = body[picture_url_start:picture_url_start + picture_url_len]
    picture_url = picture_url.replace('&amp;', '&')
    return picture_url


def _get_meteoblue_tz(body: str) -> str:
    utc_timezone_starts = [m.start() for m in re.finditer(cfg.METEOBLUE_TIMEZONE_PLUS_PREFIX, body)] 
    if not utc_timezone_starts:
        utc_timezone_starts = [m.start() for m in re.finditer(cfg.METEOBLUE_TIMEZONE_MINUS_PREFIX, body)]             
    if not utc_timezone_starts:
        gmt_timezone_starts = [m.start() for m in re.finditer(cfg.METEOBLUE_TIMEZONE_GMT, body)]             
        if len(gmt_timezone_starts) == 1:
            utc_timezone = "+00:00"
            return utc_timezone
        wet_timezone_starts = [m.start() for m in re.finditer(cfg.METEOBLUE_TIMEZONE_WET, body)]             
        if len(wet_timezone_starts) == 1:
            utc_timezone = "+00:00"
            return utc_timezone

    if len(utc_timezone_starts) != 1:
        starts = [body[i:i + 100] for i in utc_timezone_starts]
        return ''    
    
    utc_timezone_start = utc_timezone_starts[0]
    utc_timezone = body[utc_timezone_start + 4: utc_timezone_start + 10]
    return utc_timezone


def _get_meteoblue_water_temp(body: str) -> Optional[int]:
    water_temp_node_starts = [m.start() for m in re.finditer(cfg.METEOBLUE_WATER_TEMP_NODE_TITLE, body)] 
    if not water_temp_node_starts:
        return None
    water_node_start = water_temp_node_starts[0]
    body = body[water_node_start:]
    temp_block_starts = [m.start() for m in re.finditer(cfg.METEOBLUE_WATER_TEMP_BLOCK_START, body)]
    if not temp_block_starts:
        return None
    temp_block_start = temp_block_starts[0]
    body = body[temp_block_start + len(cfg.METEOBLUE_WATER_TEMP_BLOCK_START):]
    
    temp_block_ends = [m.start() for m in re.finditer(cfg.METEOBLUE_WATER_TEMP_BLOCK_END, body)]
    if not temp_block_ends:
        return None
    temp_block_end = temp_block_ends[0]
    
    temp_str = body[:temp_block_end]
    if temp_str.isdigit() or temp_str[0] == '-' and temp_str[1:].isdigit():
        temperature = int(temp_str)
        return temperature
    
    return None
    
    # if not utc_timezone_starts:
    
def _get_meteoblue_sunrise_and_sunset(body: str) \
        -> tuple[Optional[TimeOfDay], Optional[TimeOfDay]]:
    
    sunrise_block_starts = [m.start() for m in re.finditer(cfg.METEOBLUE_SUNRISE_BLOCK_START, body)] 
    if len(sunrise_block_starts) != 1:
        return None, None
    sunrise_block_start = sunrise_block_starts[0]
    body = body[sunrise_block_start + len(cfg.METEOBLUE_SUNRISE_BLOCK_START):]
    sunrise_str = body[:5]
    sunrise = parse_time(sunrise_str)
    
    sunset_block_starts = [m.start() for m in re.finditer(cfg.METEOBLUE_SUNSET_BLOCK_START, body)] 
    if len(sunset_block_starts) != 1:
            return None, None
    sunset_block_start = sunset_block_starts[0]
    body = body[sunset_block_start + len(cfg.METEOBLUE_SUNSET_BLOCK_START):]
    sunset_str = body[:5]
    sunset = parse_time(sunset_str)
    
    return sunrise, sunset
            

def _get_meteoblue_pic_url_tz_temp_sun(url_suffix_for_sig: str, dark_mode: bool) \
        -> tuple[str, str, Optional[int], 
                 Optional[TimeOfDay], Optional[TimeOfDay]]:
    url = cfg.METEOBLUE_GET_CITI_INFO_PREFIX + url_suffix_for_sig
    dark_mode = str(dark_mode).lower()
    cookies = cfg.METEOBLUE_COOKIES
    cookies['darkmode'] = dark_mode
    response = requests.get(url, cookies=cookies)
    body = response.text

    utc_timezone = _get_meteoblue_tz(body)
    water_temperature = _get_meteoblue_water_temp(body)
    sunrise, sunset = _get_meteoblue_sunrise_and_sunset(body)
    picture_url = _get_meteoblue_pic_url(body)
    
    return picture_url, utc_timezone, water_temperature, sunrise, sunset


def _crop_image(image_bytes: io.BytesIO) -> io.BytesIO:
    image = Image.open(image_bytes)
    h_1 = 600
    h_2 = h_1 + (image.height - h_1) // 2
    h_3 = h_2 + (image.height - h_1) // 2
    area_1 = (0, 0, image.width, h_1)
    area_2 = (0, h_1, image.width, h_2)
    area_3 = (0, h_2, image.width, h_3)
    cropped_3 = image.crop(area_3)
    image.paste(cropped_3, area_2)
    result = image.crop((0, 0, image.width, h_2))
    
    cropped_bytes_object = io.BytesIO()
    result.save(cropped_bytes_object, format='png')
    cropped_bytes_object.seek(0)
    utils.print_with_time(f'    cropped picture')
    return cropped_bytes_object


def _get_weather_image_tz_temp_sun(city: City, dark_mode: bool) \
        -> tuple[io.BytesIO, str, Optional[int], 
                 Optional[TimeOfDay], Optional[TimeOfDay]]:
    # utils.print_with_time(f'    START getting picture url')
    picture_url, tz, temp, sunrise, sunset \
            = _get_meteoblue_pic_url_tz_temp_sun(city.url_suffix_for_sig, dark_mode)
    utils.print_with_time(f'    got picture url')
    # utils.print_with_time(f'    START getting picture')
    response = requests.get(picture_url)
    utils.print_with_time(f'    got picture')
    # utils.print_with_time(f'    START cropping picture')
    image_bytes = io.BytesIO(response.content)
    cropped_image_bytes = _crop_image(image_bytes)
    return cropped_image_bytes, tz, temp, sunrise, sunset


def _get_openweathermap_coordinates_and_name(city_name: str) -> tuple[str, str]:
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