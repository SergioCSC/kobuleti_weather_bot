import config as cfg
import api_keys

import requests
import io
import sys
from urllib.error import HTTPError


def is_in_debug_mode():
    gettrace = getattr(sys, 'gettrace', None)
    return bool(gettrace and gettrace())


def send_message(chat_set: set[int], message: str, image: io.BytesIO) -> None:
    # photo_url = 'https://my.meteoblue.com/visimage/meteogram_web_hd?look=KILOMETER_PER_HOUR%2CCELSIUS%2CMILLIMETER%2Cdarkmode&apikey=5838a18e295d&temperature=C&windspeed=kmh&precipitationamount=mm&winddirection=3char&city=K%27obulet%27i&iso2=ge&lat=41.8214&lon=41.7792&asl=3&tz=Asia%2FTbilisi&lang=en&sig=a4868efb7f837c79aa59b5b95505a0b1'
    # photo_url = 'https://www.fnordware.com/superpng/pnggrad16rgb.png'

    for chat_id in chat_set:
        TELEGRAM_SITE = (
            f'{cfg.TELEGRAM_URL_PREFIX}'
            f'{api_keys.TELEGRAM_BOT_TOKEN}'
            f'/sendPhoto'
            f'?disable_notification=true'
            f'&parse_mode=MarkdownV2'
            f'&chat_id={chat_id}'
            f'&caption={message}'
        )
        print(TELEGRAM_SITE)
        image.seek(0)
        try:
            result = requests.post(TELEGRAM_SITE, files={'photo': image})
            if result.status_code != 200:
                print(f'{TELEGRAM_SITE = }\n{result.text = }')
        except HTTPError as e:
            print(f'HTTPError for url: {TELEGRAM_SITE}\n\nException: {e}')
    
    image.seek(0)