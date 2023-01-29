import config as cfg
import utils
import base
import weather_connector
import tg_api_connector
from not_found_messages import not_found_weather_texts
from not_found_messages import not_found_weather_image_text

import io
import json
import tests
import random
from enum import Enum, auto
from typing import NamedTuple, Optional
from functools import cache


class EventType(Enum):
    SCHEDULED = auto()
    CITY = auto()
    SWITCH_DARKMODE = auto()
    OTHER = auto()


class EventData(NamedTuple):
    type: EventType
    chat_id: int
    city_name: str


def parse_event(event) -> EventData:
    default_city_name = cfg.DEFAULT_CITY
    if event.get('detail-type') == 'Scheduled Event':  # event initiated by Event Bridge
        return EventData(EventType.SCHEDULED, None, None)
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
            # message_type = update[key].get('entities',[{}])[0].get('type')
            
            text = update[key].get('text', '')
            if not text:
                return EventData(EventType.OTHER, None, None)
            text = bytes(text, 'utf-8').decode('utf-8').strip()
            
            bot_mention_position = text.find(f'@{cfg.BOT_NAME}')
            if bot_mention_position != -1:
                text = text[:bot_mention_position].strip()
            
            if text == '/dark':
                return EventData(EventType.SWITCH_DARKMODE, chat_id, None)
            
            is_private = update[key]['chat'].get('type') == 'private'
            if is_private and not text.startswith('/'):
                text = '/' + text

            if text.startswith('/') and len(text) > 2:  # city command
                text = text[1:].strip()
                city_name = text.strip()
                if len(city_name) > 1: 
                    # base.add_???(???) TODO
                    return EventData(EventType.CITY, chat_id, city_name)
            return EventData(EventType.CITY, chat_id, default_city_name)
    return EventData(EventType.OTHER, None, None)


@cache
def create_message(city_name: str, dark_mode: bool) -> \
        tuple[str, Optional[io.BytesIO]]:
    weather_text = weather_connector.get_weather_text(city_name)
    weather_image = weather_connector.get_weather_image(city_name, dark_mode)
    
    not_found_start = f'{city_name}, говорите ... \n\n'
    
    if weather_text == '':
        text_body = random.choice(not_found_weather_texts)
        weather_text = not_found_start + text_body

    if weather_image is None:
        if not weather_text.startswith(not_found_start):
            weather_text += not_found_weather_image_text
    
    return weather_text, weather_image


def lambda_handler(event: dict, context) -> dict:
    event_data = parse_event(event)
    
    success = {'statusCode': 200, 'body': 'Success'}
    
    if event_data.type is EventType.OTHER:
        return success
    
    elif event_data.type is EventType.SWITCH_DARKMODE:
        chat_id = event_data.chat_id
        dark_mode = base.switch_darkmode(chat_id)
        text = f'Теперь картинка будет {"тёмная" if dark_mode else "светлая"}'
        tg_api_connector.send_message({chat_id}, text, None)
        return success
    
    elif event_data.type is EventType.SCHEDULED:
        chats_with_params = base.get_chats_with_params()
        for chat_info in chats_with_params:
            chat_id = chat_info['id']
            dark_mode = chat_info.get('dark_mode', False)
            city_names = chat_info.get('cities', [cfg.DEFAULT_CITY])
            for city_name in city_names:
                text, image = create_message(city_name, dark_mode)
                tg_api_connector.send_message({chat_id}, text, image)
    
    elif event_data.type is EventType.CITY:
        chat_id = event_data.chat_id
        city_name = event_data.city_name
        
        chats_with_params = base.get_chats_with_params()
        base.add_chat(chat_id)
        
        dark_mode = cfg.DEFAULT_DARKMODE
        for chat_info in chats_with_params:
            if chat_info['id'] == chat_id:
                dark_mode = chat_info.get('dark_mode', cfg.DEFAULT_DARKMODE)
                break
        
        text, image = create_message(city_name, dark_mode)
        tg_api_connector.send_message({chat_id}, text, image)
    else:
        assert False
    
    utils.print_with_time(f'sent messages to chats')
    return success


if __name__ == '__main__':
    for k, v in tests.__dict__.items():
        if k.startswith('test_') and isinstance(v, dict):
            lambda_handler(v, None)