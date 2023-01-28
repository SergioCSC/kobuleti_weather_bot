import config as cfg
import utils
import base
import weather_connector
import tg_api_connector
from not_found_messages import not_found_weather_messages

import io
import json
import tests
import random

        
def get_city_and_chats(event) -> tuple[str, set[int]]:
    default_city_name = cfg.DEFAULT_CITY
    if event.get('detail-type') == 'Scheduled Event':  # event initiated by Event Bridge
        return default_city_name, base.get_chat_set()  # TODO
    elif event.get('httpMethod') in (
        'GET',
        'POST',
    ):  # event initiated by telegram via http api gateway
        update = event.get('body')
        assert update
        update = json.loads(update)
        utils.print_with_time(update)
        key = 'message'
        if key in update:
            chat_id = int(update[key]['chat']['id'])
            base.add_chat(chat_id)
            # message_type = update[key].get('entities',[{}])[0].get('type')
            
            text = update[key].get('text', '')
            if not text:
                return '', {}
            text = bytes(text, 'utf-8').decode('utf-8')
            if text.startswith('/') and len(text) > 2:  # city command
                text = text[1:].strip()
                bot_mention_position = text.find(f'@{cfg.BOT_NAME}')
                if bot_mention_position != -1:
                    text = text[:bot_mention_position]
                city_name = text.strip()
                if len(city_name) > 1: 
                    # base.add_???(???) TODO
                    return city_name, {chat_id}
            return default_city_name, {chat_id}
    return '', {}


def lambda_handler(event: dict, context) -> dict:
    city_name, chat_set = get_city_and_chats(event)
    if not city_name:
        return {'statusCode': 200, 'body': 'Success'}
    utils.print_with_time(f'{city_name = }')
    try:
        # utils.print_with_time(f'START got text from openweathermap.org')
        weather = weather_connector.http_get_weather(city_name)
        message = weather_connector.create_weather_message(weather)
        utils.print_with_time(f'got text from openweathermap.org')
    except Exception as e:
        utils.print_with_time(f'Exception {e} in weather_connector.http_get_weather({city_name})')
        message = random.choice(not_found_weather_messages)
    try:
        # utils.print_with_time(f'START got image from meteoblue.com')
        image: io.BytesIO = weather_connector.get_weather_image(city_name)
        # utils.print_with_time(f'got image from meteoblue.com')
    except Exception as e:
        utils.print_with_time(f'Exception {e} in weather_connector.get_weather_image({city_name})')
        image = None
        if message not in not_found_weather_messages:
            message += '\n\nМожно ваш паспорт? Спасибо. Таааак ...' \
                ' Галя, не видишь, я занята. Что там у вас  ... аааа, ну конечно!' \
                ' А вы вообще в курсе, что вам никакие графики никаких температур не положены?' \
                ' Да, совсем. Не задерживайте очередь.' \
                ' Если вам так надо,' \
                ' подходите завтра к 8 утра в регистратуру с анализами.' \
                ' За результатами через 60 рабочих дней. Что вам ещё?' \
                ' Нет, через госуслуги нельзя. До свидания.\n\nИшь, прогноз погоды им подавай'
    # utils.print_with_time(f'START sending messages to chats')
    tg_api_connector.send_message(chat_set, message, image)
    utils.print_with_time(f'sent messages to chats')
    return {'statusCode': 200, 'body': 'Success'}


if __name__ == '__main__':
    for k, v in tests.__dict__.items():
        if k.startswith('test_') and isinstance(v, dict):
            lambda_handler(v, None)