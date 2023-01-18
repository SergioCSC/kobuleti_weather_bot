import json

import sys
from datetime import datetime
import http
import urllib
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def is_in_debug_mode():
    gettrace = getattr(sys, 'gettrace', None)
    return bool(gettrace and gettrace())

# SITE = os.environ['site']  # URL of the site to check, stored in the site environment variable
# EXPECTED = os.environ['expected']  # String expected to be on the page, stored in the expected environment variable


# def validate(res):
#     '''Return False to trigger the canary

#     Currently this simply checks whether the EXPECTED string is present.
#     However, you could modify this to perform any number of arbitrary
#     checks on the contents of SITE.
#     '''
#     return EXPECTED in res

TELEGRAM_URL_PREFIX = 'https://api.telegram.org/bot'
BOT_TOKEN = '5887622494:AAEvqObQZf6AE8F7oOYrPCiV11r_t8siWrw'


def get(url: str) -> http.client.HTTPResponse:
    req = Request(url, headers={'User-Agent': 'AWS Lambda'})
    return urlopen(req)



def get_chat_list() -> set[int]:
    UPDATES_URL = TELEGRAM_URL_PREFIX + BOT_TOKEN + '/getUpdates'
    result = get(UPDATES_URL)
    d = json.load(result)

    if 'ok' not in d or d['ok'] != True:
        print('no urls')
        return
    updates = d['result']
    result = set()
    for update in updates:
        update_body = None
        for key in ('message',
                    'edited_message',
                    'chat_member', 
                    'my_chat_member',
                    'chat_join_request',
                    'channel_post',
                    'edited_channel_post'
                    ):
            if not update_body:
                update_body = update.get(key)
        result.add(int(update_body['chat']['id']))
    
    if is_in_debug_mode():
        result = {-1001899507998}  # test group for bots
    return result
    


def lambda_handler(event, context):
    # WEATHER_SITE = 'http://dataservice.accuweather.com/currentconditions/v1/166879?apikey=Gvz2sY3fAxES8GHGVZeaoGsfwxVJA3gE'
    WEATHER_SITE = 'https://api.openweathermap.org/data/2.5/weather?lat=41.8141&lon=41.7739&units=metric&lang=ru&appid=11c0d3dc6093f7442898ee49d2430d20'
    print('Checking {} at {}...'.format(WEATHER_SITE, event['time']))
    result = get(WEATHER_SITE)
    # return event['time']
    d = json.load(result)
    # celsius = d[0]['Temperature']['Metric']['Value']
    # weather_text = d[0]['WeatherText']
    celsius = float(d['main']['temp'])  # - 273.15
    pressure_mm_hg = int(float(d['main']['pressure']) * 3 / 4)
    humidity = d['main']['humidity']
    wind_speed = d['wind']['speed']
    weather_text = d['weather'][0]['description']
    result = f'Кобулети\n' \
            f'температура {celsius:.1f} °C\n' \
            f'влажность {humidity}%\n' \
            f'скорость ветра {wind_speed} м/с\n' \
            f'давление {pressure_mm_hg} мм рт. ст.\n' \
            f'{weather_text}'
    result = urllib.parse.quote(result.encode('utf-8'))
    for chat_id in get_chat_list():
        TELEGRAM_SITE = f'{TELEGRAM_URL_PREFIX}{BOT_TOKEN}/sendMessage?' \
                f'disable_notification=true&chat_id={chat_id}&text={result}'
        print(TELEGRAM_SITE)
        try:
            get(TELEGRAM_SITE)
        except HTTPError as e:
            print(f'HTTPError for url: {TELEGRAM_SITE}\n\nException: {e}')
    return
    

if __name__ == '__main__':
    test_event = {
        "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "123456789012",
        "time": "1970-01-01T00:00:00Z",
        "region": "us-east-1",
        "resources": [
            "arn:aws:events:us-east-1:123456789012:rule/ExampleRule"
        ],
        "detail": {}
    }
    
    lambda_handler(test_event, None)