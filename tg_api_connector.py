import sys
import http
from urllib.request import Request, urlopen
from urllib.error import HTTPError


TELEGRAM_URL_PREFIX = 'https://api.telegram.org/bot'
BOT_TOKEN = '5887622494:AAEvqObQZf6AE8F7oOYrPCiV11r_t8siWrw'


def is_in_debug_mode():
    gettrace = getattr(sys, 'gettrace', None)
    return bool(gettrace and gettrace())


def get(url: str) -> http.client.HTTPResponse:
    req = Request(url, headers={'User-Agent': 'AWS Lambda'})
    return urlopen(req)


def send_message(chat_set: set[int], message: str) -> None:

    for chat_id in chat_set:
        TELEGRAM_SITE = (
            f'{TELEGRAM_URL_PREFIX}{BOT_TOKEN}/sendMessage?'
            f'disable_notification=true&chat_id={chat_id}&text={message}'
        )
        print(TELEGRAM_SITE)
        try:
            get(TELEGRAM_SITE)
        except HTTPError as e:
            print(f'HTTPError for url: {TELEGRAM_SITE}\n\nException: {e}')