import config as cfg
import messages
import utils
import api_keys

import requests
import io
import json
import urllib
from urllib.error import HTTPError
from typing import Optional


USER_LOCATION_KEYBOARD = [[{"text": messages.BUTTON_WEATHER_HERE_TEXT, 
                            "request_location": True}]]
USER_LOCATION_MARKUP = {"keyboard": USER_LOCATION_KEYBOARD,
                        "one_time_keyboard": True,
                        #  "is_persistent": True,
                         "resize_keyboard": True,            
                        }
USER_LOCATION_STR = json.dumps(USER_LOCATION_MARKUP)

REMOVE_KEYBOARD_MARKUP = {"remove_keyboard": True}
REMOVE_KEYBOARD_MARKUP_STR = json.dumps(REMOVE_KEYBOARD_MARKUP)


def send_message(message_to: str,
                 chat_set: set[int],
                 message: str,
                 image: Optional[io.BytesIO],
                 reply_buttons_count: Optional[int] = None,
                 location_str: str = '',
                 want_user_location: bool = False,
                 ) -> None:

    for chat_id in chat_set:
        if message:
            for c in '[]()~`>#+-=|{}.!':  # '_*[]()~`>#+-=|{}.!':  # '!=()#-.':
                message = message.replace(c, '\\' + c)
            if message_to and str(chat_id).startswith('-100'):
                if len(message_to.split('&')) != 2:
                    utils.print_with_time(f'{message_to = }, \
                                          {chat_id = },   {message = }')
                username, user_id = message_to.split('&')
                # message = f'{message_to},\n\n{message}'
                message = f'[{username}](tg://user?id={user_id}),\n\n{message}'

            message = urllib.parse.quote(message.encode('utf-8'))

        if location_str:
            telegram_request_url = (
                f'{cfg.TELEGRAM_URL_PREFIX}'
                f'{api_keys.TELEGRAM_BOT_TOKEN}'
                f'/sendLocation'
                f'?disable_notification=true'
                f'&chat_id={chat_id}'
                f'{location_str}'
                f'{"&reply_markup=" + REMOVE_KEYBOARD_MARKUP_STR}'
            )
        else:
            if want_user_location:
                markup = USER_LOCATION_STR
            elif reply_buttons_count:
                first_line_buttons_count = reply_buttons_count // 2
                REPLY_KEYBOARD = [[str(i) for i in range(1, first_line_buttons_count + 1)],
                                  [str(i) for i in range(first_line_buttons_count + 1, reply_buttons_count + 1)]]
                REPLY_MARKUP = {"keyboard": REPLY_KEYBOARD, 
                                "one_time_keyboard": True,
                                # "is_persistent": False,
                                "resize_keyboard": True,
                                }
                REPLY_MARKUP_STR = json.dumps(REPLY_MARKUP)
                markup = REPLY_MARKUP_STR
            else:
                markup = REMOVE_KEYBOARD_MARKUP_STR

            telegram_request_url = (
                f'{cfg.TELEGRAM_URL_PREFIX}'
                f'{api_keys.TELEGRAM_BOT_TOKEN}'
                f'/{"sendPhoto" if image else "sendMessage"}'
                f'?disable_notification=true'
                f'&parse_mode=MarkdownV2'
                f'&chat_id={chat_id}'
                f'&{"caption" if image else "text"}={message}'
                f'{"&reply_markup=" + markup}'
            )

        if image:
            image.seek(0)
        try:
            result = requests.post(telegram_request_url, 
                                   files={'photo': image} if image else {})
            utils.print_with_time(f'{telegram_request_url = }')
            if result.status_code != 200:
                utils.print_with_time(f'{telegram_request_url = }\n{result.text = }')
        except HTTPError as e:
            utils.print_with_time(f'HTTPError for url: {telegram_request_url}\n\nException: {e}')
    
    if image:
        image.seek(0)
