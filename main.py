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
from typing import Any, NamedTuple, Optional
from functools import cache


class EventType(Enum):
    SCHEDULED = auto()
    CITY = auto()
    ADD_CITIES = auto()
    CLEAR_CITIES = auto()
    SHOW_CITIES = auto()
    LIST_CITIES = auto()
    SWITCH_DARKMODE = auto()
    OTHER = auto()


class EventData(NamedTuple):
    type: EventType
    chat_id: int
    city_names: list[str]


def parse_event(event) -> EventData:
    default_city_name = cfg.DEFAULT_CITY
    if event.get('detail-type') == 'Scheduled Event':  # event initiated by Event Bridge
        return EventData(EventType.SCHEDULED, None, [])
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
                return EventData(EventType.OTHER, None, [])
            text = bytes(text, 'utf-8').decode('utf-8').strip()
            
            is_private = update[key]['chat'].get('type') == 'private'
            if is_private and not text.startswith('/'):
                text = '/' + text

            bot_mention_position = text.find(f'@{cfg.BOT_NAME}')
            if bot_mention_position != -1:
                text = text[:bot_mention_position].strip()

            if text == '/dark':
                return EventData(EventType.SWITCH_DARKMODE, chat_id, [])
            
            if text == '/clear':
                return EventData(EventType.CLEAR_CITIES, chat_id, [])
            
            if text == '/list':
                return EventData(EventType.LIST_CITIES, chat_id, [])
            
            if text == '/show':
                return EventData(EventType.SHOW_CITIES, chat_id, [])
            
            if text.startswith('/add'):
                city_names = text[len('/add'):].strip().split(',')
                city_names = [city.strip() for city in city_names if city]
                return EventData(EventType.ADD_CITIES, chat_id, city_names)

            
            if text.startswith('/') and len(text) > 2:  # city command
                text = text[1:].strip()
                city_name = text.strip()
                if len(city_name) > 1:
                    return EventData(EventType.CITY, chat_id, [city_name])
            return EventData(EventType.CITY, chat_id, [default_city_name])
    return EventData(EventType.OTHER, None, [])


def update_db(event_data: EventData) -> Any:
    if event_data.type is EventType.SWITCH_DARKMODE:
        feedback = base.switch_darkmode(event_data.chat_id)
    elif event_data.type is EventType.ADD_CITIES:
        feedback = base.add_cities(event_data.chat_id, event_data.city_names)
    elif event_data.type is EventType.CLEAR_CITIES:
        feedback = base.clear_cities(event_data.chat_id)
    else:
        assert False
    return feedback
    

def lambda_handler(event: dict, context) -> dict:
    event_data = parse_event(event)
    
    success = {'statusCode': 200, 'body': 'Success'}
    
    if event_data.type is EventType.OTHER:
        return success
    elif event_data.type is EventType.SCHEDULED:
        chats_with_params = base.get_chats_with_params()
        for chat_id, chat_info in chats_with_params.items():
            dark_mode = chat_info.get('dark_mode', cfg.DEFAULT_DARKMODE)
            city_names = chat_info.get('cities', [])
            for city_name in city_names:
                text, image = create_message(city_name, dark_mode)
                tg_api_connector.send_message({chat_id}, text, image)
        return success

    if event_data.type in (EventType.SWITCH_DARKMODE, EventType.ADD_CITIES, EventType.CLEAR_CITIES):
        db_update_feedback = update_db(event_data)

    assert event_data.type in (EventType.ADD_CITIES, EventType.CITY, EventType.CLEAR_CITIES, 
            EventType.LIST_CITIES, EventType.SHOW_CITIES, EventType.SWITCH_DARKMODE)

    chat_id = event_data.chat_id
    
    if event_data.type is EventType.SWITCH_DARKMODE:
        dark_mode = db_update_feedback
        text = f'Теперь картинка будет {"тёмная" if dark_mode else "светлая"}'
        tg_api_connector.send_message({chat_id}, text, None)
        return success
    
    assert event_data.type in (EventType.ADD_CITIES, EventType.CLEAR_CITIES, 
            EventType.LIST_CITIES, EventType.SHOW_CITIES, EventType.CITY)
    
    if event_data.type in (EventType.CLEAR_CITIES, EventType.ADD_CITIES):
        if event_data.type is EventType.CLEAR_CITIES:
            text = f'Напоминалки обо всех городах удалены'
        elif event_data.type is EventType.ADD_CITIES:
            city_names = event_data.city_names
            old_without_new_cities = db_update_feedback
            if not city_names or not city_names[0]:
                text = f'Здравствуйте. Кажется, вы нажали команду\n\n/add\n\nв меню.' \
                        f' Вам-то хорошо, нажали и нажали. А наш департамент' \
                        f' на ушах: все хотят знать, какой город вы хотите добавить' \
                        f' в напоминалки. Все бегают, шумят, волосы рвут. ' \
                        f' Ставки делают, морды бьют. И никто ничего' \
                        f' не знает, никто не за что не отвечает. Что за народ!' \
                        f' можно вас попросить сказать им уже город, а то они всё тут разнесут?' \
                        f' Ну, например, так: \n\n/add Ярославль'
            else:
                text = f'Буду напоминать о {", ".join(city_names)} по утрам'
                if old_without_new_cities:
                    text += '. A ещё о ' + ', '.join(old_without_new_cities)
        
        tg_api_connector.send_message({chat_id}, text, None)
        return success

    assert event_data.type in (EventType.LIST_CITIES, EventType.SHOW_CITIES, EventType.CITY)
    
    chats_with_params = base.get_chats_with_params()
    
    if event_data.type is EventType.LIST_CITIES:
        city_names = chats_with_params.get(chat_id, {}).get('cities', [])
        if not city_names:
            text = f'Вы просили напоминать о пустом множестве городов! Будет сделано! 🫡'
        else:
            text = f'Кажется, вы просили напоминать о ' + ', '.join(city_names) + '. Ох, всего-то не упомнишь ...'
        
        tg_api_connector.send_message({chat_id}, text, None)
        return success

    assert event_data.type in (EventType.CITY, EventType.SHOW_CITIES)
    
    if event_data.type is EventType.CITY:
        city_names = event_data.city_names
        if len(city_names) == 1 and city_names[0] == 'city':
            text = 'Добро пожаловать на метеостанцию. Располагайтесь,' \
                f' чайку? Унты не ставьте близко к камину, сядут-с ... ' \
                f' Вы какие сигары предпочитаете, La Gloria Cubana? Romeo y Julieta?' \
                f' Простите, конечно, перехожу к вашему делу.' \
                f' Вы точно хотите послать гонцов в город city? Нет, мои парни могут' \
                f' и не такое, и собаки хорошо отдохнули. Только, вот, не хотите ли,' \
                f' вместо мифического\n\n/city\n\n, узнать погоду в городе\n\n/Оймякон\n\n' \
                f'? Или, допустим, в\n\n/Могадишо\n\n? Вы, кстати, были в Могадишо?' \
                f' Я вот вам очень советую. Очень, знаете ли, хорошее место, чтобы там' \
                f' не бывать. Я вот там не был и видите, как мне это понравилось ...' \
                f' Эх, да ... Вот же ж какого времени не было ... Хорошо.'
            tg_api_connector.send_message({chat_id}, text, None)
            return success    
    elif event_data.type is EventType.SHOW_CITIES:
        city_names = chats_with_params.get(chat_id, {}).get('cities', [])
    
    if not city_names:
        text = 'Сейчас-сейчас ... бегу ... ой, а ни одного' \
                f' города-то вы и не заказывали ...'        
        tg_api_connector.send_message({chat_id}, text, None)
        return success
    
    dark_mode = chats_with_params.get(chat_id, {}).get('dark_mode', cfg.DEFAULT_DARKMODE)
    
    for city_name in city_names:
        text, image = create_message(city_name, dark_mode)
        tg_api_connector.send_message({chat_id}, text, image)

    return success






    
    # elif event_data.type is EventType.SWITCH_DARKMODE:
    #     chat_id = event_data.chat_id
    #     dark_mode = base.switch_darkmode(chat_id)
    #     text = f'Теперь картинка будет {"тёмная" if dark_mode else "светлая"}'
    #     tg_api_connector.send_message({chat_id}, text, None)
    
    # elif event_data.type is EventType.SCHEDULED:
    #     # if event_data.chat_id:
    #     #     chat_id = event_data.chat_id
    #     #     chats_with_params = base.get_chat_with_params(chat_id)
    #     #     if not chats_with_params or not chats_with_params[0].get('cities'):
    #     #         text = 'Сейчас-сейчас ... бегу ... ой, а ни одного' \
    #     #                 f' города-то вы и не заказывали ...'
    #     #         tg_api_connector.send_message({chat_id}, text, None)
    #     # else:
    #     #     chats_with_params = base.get_chats_with_params()
        
    #     for chat_info in chats_with_params:
    #         chat_id = chat_info['id']
    #         dark_mode = chat_info.get('dark_mode', False)
    #         city_names = chat_info.get('cities', [])
    #         for city_name in city_names:
    #             text, image = create_message(city_name, dark_mode)
    #             tg_api_connector.send_message({chat_id}, text, image)
    
    # elif event_data.type is EventType.CITY:
    #     chat_id = event_data.chat_id
    #     city_name = event_data.city_names[0]
        
    #     chats_with_params = base.get_chats_with_params()
    #     base.add_chat(chat_id)
        
    #     dark_mode = cfg.DEFAULT_DARKMODE
    #     for chat_info in chats_with_params:
    #         if chat_info['id'] == chat_id:
    #             dark_mode = chat_info.get('dark_mode', cfg.DEFAULT_DARKMODE)
    #             break
        
    #     text, image = create_message(city_name, dark_mode)
    #     tg_api_connector.send_message({chat_id}, text, image)
        
    # elif event_data.type is EventType.ADD_CITIES:
    #     chat_id = event_data.chat_id
    #     city_names = event_data.city_names

    #     old_without_new_cities = base.add_cities(chat_id, city_names)
    #     text = f'Буду напоминать о {", ".join(city_names)} по утрам'
    #     if old_without_new_cities:
    #         text += '. A ещё о ' + ', '.join(old_without_new_cities)
        
    #     tg_api_connector.send_message({chat_id}, text, None)
    # elif event_data.type is EventType.CLEAR_CITIES:
    #     chat_id = event_data.chat_id
        
    #     base.clear_cities(chat_id)
    #     text = f'Напоминалки обо всех городах удалены'
    #     tg_api_connector.send_message({chat_id}, text, None)
        
    # elif event_data.type is EventType.LIST_CITIES:
    #     chat_id = event_data.chat_id
    #     cities = base.list_cities(chat_id)
    #     if not cities:
    #         text = f'Вы просили напоминать о пустом множестве городов! Будет сделано! 🫡'
    #     else:
    #         text = f'Кажется, вы просили напоминать о ' + ', '.join(cities) + '. Ох, всего-то не упомнишь ...'
        
    #     tg_api_connector.send_message({chat_id}, text, None)
        
    # else:
    #     assert False

    # utils.print_with_time(f'sent messages to chats')
    # return success


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


if __name__ == '__main__':
    for k, v in tests.__dict__.items():
        if k.startswith('test_') and isinstance(v, dict):
            lambda_handler(v, None)