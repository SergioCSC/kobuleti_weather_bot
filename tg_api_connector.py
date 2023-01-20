import config as cfg
import api_keys
import utils

import sys
from urllib.error import HTTPError


def is_in_debug_mode():
    gettrace = getattr(sys, 'gettrace', None)
    return bool(gettrace and gettrace())


def send_message(chat_set: set[int], message: str) -> None:

    for chat_id in chat_set:
        TELEGRAM_SITE = (
            f'{cfg.TELEGRAM_URL_PREFIX}{api_keys.TELEGRAM_BOT_TOKEN}/sendMessage?'
            f'disable_notification=true&chat_id={chat_id}&text={message}'
        )
        print(TELEGRAM_SITE)
        try:
            utils.get(TELEGRAM_SITE)
        except HTTPError as e:
            print(f'HTTPError for url: {TELEGRAM_SITE}\n\nException: {e}')