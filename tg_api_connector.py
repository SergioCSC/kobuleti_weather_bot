import config as cfg
import utils
import api_keys

import requests
import io
import sys
import urllib
from urllib.error import HTTPError
from typing import Optional


def send_message(chat_set: set[int], message: str, image: Optional[io.BytesIO]) -> None:
    message = message.replace('!', '\!')
    message = urllib.parse.quote(message.encode('utf-8'))
    message = message.replace('-', '\-')
    message = message.replace('.', '\.')
    
    for chat_id in chat_set:
        telegram_request_url = (
            f'{cfg.TELEGRAM_URL_PREFIX}'
            f'{api_keys.TELEGRAM_BOT_TOKEN}'
            f'/{"sendPhoto" if image else "sendMessage"}'
            f'?disable_notification=true'
            f'&parse_mode=MarkdownV2'
            f'&chat_id={chat_id}'
            f'&{"caption" if image else "text"}={message}'
        )
        if image:
            image.seek(0)
        try:
            utils.print_with_time(f'before sending telegram message')
            result = requests.post(telegram_request_url, 
                                   files={'photo': image} if image else {})
            utils.print_with_time(f'{telegram_request_url = }')
            if result.status_code != 200:
                utils.print_with_time(f'{telegram_request_url = }\n{result.text = }')
        except HTTPError as e:
            utils.print_with_time(f'HTTPError for url: {telegram_request_url}\n\nException: {e}')
    
    if image:
        image.seek(0)