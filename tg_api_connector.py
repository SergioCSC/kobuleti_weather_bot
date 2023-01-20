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
            f'{cfg.TELEGRAM_URL_PREFIX}'
            f'{api_keys.TELEGRAM_BOT_TOKEN}'
            f'/sendMessage'
            f'?disable_notification=true'
            f'&parse_mode=MarkdownV2'
            f'&chat_id={chat_id}'
            f'&text={message}'
        )
        print(TELEGRAM_SITE)
        try:
            utils.get(TELEGRAM_SITE)
        except HTTPError as e:
            print(f'HTTPError for url: {TELEGRAM_SITE}\n\nException: {e}')