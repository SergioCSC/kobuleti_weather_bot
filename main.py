import config as cfg
import utils
from city import City
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
    ADD_CITY = auto()
    CHOOSE_CITY = auto()
    CLEAR_CITIES = auto()
    SHOW_CITIES = auto()
    LIST_CITIES = auto()
    SWITCH_DARKMODE = auto()
    OTHER = auto()


class EventData(NamedTuple):
    type: EventType
    chat_id: Optional[int]
    city_name: str
    city_num: Optional[int]


def parse_event(event) -> EventData:
    default_city_name = cfg.DEFAULT_CITY
    if event.get('detail-type') == 'Scheduled Event':  # event initiated by Event Bridge
        return EventData(EventType.SCHEDULED, None, '', None)
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
                return EventData(EventType.OTHER, None, '', None)
            text = bytes(text, 'utf-8').decode('utf-8').strip()
            
            is_private = update[key]['chat'].get('type') == 'private'
            if is_private and not text.startswith('/'):
                text = '/' + text

            bot_mention_position = text.find(f'@{cfg.BOT_NAME}')
            if bot_mention_position != -1:
                text = text[:bot_mention_position].strip()

            if text == '/dark':
                return EventData(EventType.SWITCH_DARKMODE, chat_id, '', None)
            
            if text == '/clear':
                return EventData(EventType.CLEAR_CITIES, chat_id, '', None)
            
            if text == '/list':
                return EventData(EventType.LIST_CITIES, chat_id, '', None)
            
            if text == '/show':
                return EventData(EventType.SHOW_CITIES, chat_id, '', None)
            
            if text.startswith('/add'):
                city_name = text[len('/add'):].strip()
                return EventData(EventType.ADD_CITY, chat_id, city_name, None)

            if text.startswith('/') and text[1:].strip().isdigit():
                number = int(text[1:].strip())
                return EventData(EventType.CHOOSE_CITY, chat_id, None, number)

            if text.startswith('/') and len(text) > 2:  # city command
                city_name = text[1:].strip()
                if len(city_name) > 1:
                    return EventData(EventType.CITY, chat_id, city_name, None)
            
            if text == '/k':
                return EventData(EventType.CITY, chat_id, default_city_name, None)
    return EventData(EventType.OTHER, None, '', None)
    

def lambda_handler(event: dict, context) -> dict:
    event_data = parse_event(event)
    
    success = {'statusCode': 200, 'body': 'Success'}
    
    if event_data.type is EventType.OTHER:
        return success
    elif event_data.type is EventType.SCHEDULED:
        chats = base.get_chats()
        for chat_id, chat_info in chats.items():
            dark_mode = chat_info.get('dark_mode', cfg.DEFAULT_DARKMODE)
            cities = chat_info.get('cities', [])
            for city in cities:
                city_name = city.local_name if isinstance(city, City) else city
                # TODO fix upper line
                
                text, image = create_message(city, dark_mode)
                tg_api_connector.send_message({chat_id}, text, image)
        return success
    
    chat_id = event_data.chat_id
    
    # if event_data.type is EventType.CHOOSE_CITY:
    #     city_num = event_data.city_num
    #     command_type, city_options = base.load_command(chat_id)
    #     chosen_city = city_options[city_num]  # TODO what if no such num ?
        
        # if command_type is EventType.CITY:
        #     pass  # TODO ???
        # elif command_type is EventType.ADD_CITY:
        #     base.add_city(chosen_city)
            
        #     city_name = chosen_city.local_name  
            
        #     text = f'Буду напоминать о {", ".join(city_name)} по утрам'
        #     # old_cities_without_new = ???  # db_update_feedback
        #     # if old_cities_without_new:
        #     #     text += '. A ещё о ' + ', '.join(old_cities_without_new)
            
        #     tg_api_connector.send_message({chat_id}, text, None)
        #     return success

        # else:
        #     assert False

    # if event_data.type in (EventType.CITY, EventType.ADD_CITY):
    #     city_options = weather_connector.get_city_options_from_name(event_data.city_name)

    #     db_update_feedback = update_db(event_data, city_options)
        
    #     text = 'Варианты: ' + ', '.join(city.local_name for city in city_options)
    #     assert isinstance(chat_id, int)
    #     tg_api_connector.send_message({chat_id}, text, None)
        
    #     return success
    
    right_city = None
    if event_data.type in (EventType.CITY, EventType.ADD_CITY):
        if not event_data.city_name:
            text = f'Здравствуйте. Кажется, вы нажали команду\n\n/add\n\nв меню.' \
                    f' Вам-то хорошо, нажали и нажали. А наш департамент' \
                    f' на ушах: все хотят знать, какой город вы хотите добавить' \
                    f' в напоминалки. Все бегают, шумят, волосы рвут. ' \
                    f' Ставки делают, морды бьют. И никто ничего' \
                    f' не знает, никто не за что не отвечает. Что за народ!' \
                    f' можно вас попросить сказать им уже город, а то они всё тут разнесут?' \
                    f' Ну, например, так: \n\n/add Ярославль'
            tg_api_connector.send_message({chat_id}, text, None)
            return success
            
        city_options = list(weather_connector.get_city_options_from_name(event_data.city_name))
        if city_options:
            right_city = city_options[0]
            if event_data.type is EventType.ADD_CITY:
                db_update_feedback = update_db(event_data, right_city)
    
    elif event_data.type in (EventType.SWITCH_DARKMODE, EventType.CLEAR_CITIES):
        db_update_feedback = update_db(event_data)

    assert event_data.type in (EventType.ADD_CITY, EventType.CITY, EventType.CLEAR_CITIES, 
            EventType.LIST_CITIES, EventType.SHOW_CITIES, EventType.SWITCH_DARKMODE)

    if event_data.type is EventType.SWITCH_DARKMODE:
        dark_mode = db_update_feedback
        text = f'Теперь картинка будет {"тёмная" if dark_mode else "светлая"}'
        tg_api_connector.send_message({chat_id}, text, None)
        return success
    
    assert event_data.type in (EventType.ADD_CITY, EventType.CLEAR_CITIES, 
            EventType.LIST_CITIES, EventType.SHOW_CITIES, EventType.CITY)
    
    if event_data.type is EventType.CLEAR_CITIES:
        text = f'Напоминалки обо всех городах удалены'
        tg_api_connector.send_message({chat_id}, text, None)
        return success
    
    if event_data.type is EventType.ADD_CITY:
        if not right_city:
            text = f'Здравствуйте. Вот ищу я, ищу ... хоть убей, нет ни одного' \
                    f' {event_data.city_name}. Странно это как-то ...'
        else:
            city_name = right_city.local_name
            old_without_new_cities = db_update_feedback
            old_without_new_cities_names = [c.local_name for c in old_without_new_cities]
            text = f'Буду напоминать о {city_name} по утрам'
            if old_without_new_cities:
                text += '. A ещё о ' + ', '.join(old_without_new_cities_names)
        
        tg_api_connector.send_message({chat_id}, text, None)
        return success

    assert event_data.type in (EventType.LIST_CITIES, EventType.SHOW_CITIES, EventType.CITY)
    
    chats = base.get_chats()
    
    if event_data.type is EventType.LIST_CITIES:
        cities = chats.get(chat_id, {}).get('cities', [])
        if not cities:
            text = f'Вы просили напоминать о пустом множестве городов!' \
                    f' Будет сделано! 🫡'
        else:
            city_names = [city.local_name for city in cities]
            text = f'Кажется, вы просили напоминать о ' \
                    + ', '.join(city_names) + '. Ох, всего-то не упомнишь ...'
        
        tg_api_connector.send_message({chat_id}, text, None)
        return success

    assert event_data.type in (EventType.CITY, EventType.SHOW_CITIES)
    
    dark_mode = chats.get(chat_id, {}).get('dark_mode', cfg.DEFAULT_DARKMODE)
    
    if event_data.type is EventType.CITY:
        if not right_city:  # TODO copypaste
            text = f'Здравствуйте. Вот ищу я, ищу ... хоть убей, нет ни одного' \
                    f' {event_data.city_name}. Странно это как-то ...'
            tg_api_connector.send_message({chat_id}, text, None)
            return success
        elif right_city.local_name == 'city':
            text = 'Добро пожаловать на метеостанцию. Располагайтесь,' \
                f' чайку? Унты не ставьте близко к камину, сядут-с ... ' \
                f' Вы какие сигары предпочитаете, La Gloria Cubana? Romeo y Julieta?' \
                f' Простите, конечно, перехожу к вашему делу.' \
                f' Вы точно хотите послать гонцов в город city? Нет, мои парни могут' \
                f' и не такое, и собаки хорошо отдохнули. Только, вот, не хотите ли,' \
                f' вместо мифического\n\n/city\n\n, узнать погоду в городе\n\n/Оймякон?\n\n' \
                f' Или, допустим, в\n\n/Могадишо\n\n? Вы, кстати, были в Могадишо?' \
                f' Я вот вам очень советую. Очень, знаете ли, хорошее место, чтобы там' \
                f' не бывать. Я вот там не был и видите, как мне это понравилось ...' \
                f' Эх, да ... Вот же ж какого времени не было ... Хорошо.'
            tg_api_connector.send_message({chat_id}, text, None)
            return success
        else:
            text, image = create_message(right_city, dark_mode)
            tg_api_connector.send_message({chat_id}, text, image)
            return success
    
    elif event_data.type is EventType.SHOW_CITIES:
        cities = chats.get(chat_id, {}).get('cities', [])

        if not cities:
            text = 'Сейчас-сейчас ... бегу ... ой, а ни одного' \
                    f' города-то вы и не заказывали ...'
                    
            tg_api_connector.send_message({chat_id}, text, None)
            return success

        for city in cities:
            text, image = create_message(city, dark_mode)
            tg_api_connector.send_message({chat_id}, text, image)
        return success

    assert False


def update_db(event_data: EventData, city: City = None) -> Any:
    if event_data.type is EventType.SWITCH_DARKMODE:
        feedback = base.switch_darkmode(event_data.chat_id)
    elif event_data.type is EventType.CLEAR_CITIES:
        feedback = base.clear_cities(event_data.chat_id)
    elif event_data.type is EventType.ADD_CITY:
        feedback = base.add_city(event_data.chat_id, city)
    # elif event_data.type in (EventType.ADD_CITY, EventType.CITY):
    #     feedback = base.save_command(event_data)
    else:
        assert False
    return feedback


@cache
def create_message(city: City, dark_mode: bool) -> \
        tuple[str, Optional[io.BytesIO]]:

    weather_text = weather_connector.get_weather_text(city)
    weather_image = weather_connector.get_weather_image(city, dark_mode)

    not_found_start = f'{city.local_name}, говорите ... \n\n'

    if weather_text == '':
        text_body = random.choice(not_found_weather_texts)
        weather_text = not_found_start + text_body

    if weather_image is None:
        if not weather_text.startswith(not_found_start):
            weather_text += not_found_weather_image_text

    return weather_text, weather_image


# if __name__ == '__main__':
#     getUpdates(timeout=30)


if __name__ == '__main__':
    for event in tests.events:
        lambda_handler(event, None)

    # for k, v in tests.__dict__.items():
    #     if k.startswith('test_') and isinstance(v, dict):
    #         lambda_handler(v, None)