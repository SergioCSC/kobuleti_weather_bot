import config as cfg
import api_keys

import requests
import io
import sys
import urllib
from urllib.error import HTTPError


def is_in_debug_mode():
    gettrace = getattr(sys, 'gettrace', None)
    return bool(gettrace and gettrace())


def send_message(chat_set: set[int], message: str, image: io.BytesIO) -> None:
    message = urllib.parse.quote(message.encode('utf-8'))
    
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