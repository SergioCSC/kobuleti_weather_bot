import config as cfg
import utils
from city import City
import base
import weather_connector
import tg_api_connector
from event import EventType, EventData
import messages

import io
import json
import tests
import random
from typing import Any, Optional
from functools import cache


def parse_event(event) -> EventData:
    default_city_name = cfg.DEFAULT_CITY
    if event.get('detail-type') == 'Scheduled Event':  # event initiated by Event Bridge
        return EventData(EventType.SCHEDULED, None, '')
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
                location = update[key].get('location')
                if location:
                    latitude = location['latitude']
                    longitude = location['longitude']
                    location_str = f'{latitude},{longitude}'
                    return EventData(EventType.USER_LOCATION, chat_id, 
                                     location_str)
                else:
                    return EventData(EventType.OTHER, None, '')
            text = bytes(text, 'utf-8').decode('utf-8').strip()
            
            is_private = update[key]['chat'].get('type') == 'private'
            if not text.startswith('/'):
                text = '/' + text

            bot_mention_position = text.find(f'@{cfg.BOT_NAME}')
            if bot_mention_position != -1:
                text = text[:bot_mention_position].strip()

            if text.lower() == '/here':
                return EventData(EventType.HERE, chat_id, '')
            
            if text.lower() == '/start':
                return EventData(EventType.START, chat_id, '')

            if text.lower() == '/dark':
                return EventData(EventType.SWITCH_DARKMODE, chat_id, '')
            
            if text.lower() == '/clear':
                return EventData(EventType.CLEAR_CITIES, chat_id, '')
            
            if text.lower() == '/list':
                return EventData(EventType.LIST_CITIES, chat_id, '')
            
            if text.lower() == '/show':
                return EventData(EventType.SHOW_CITIES, chat_id, '')
            
            if text.lower().startswith('/time'):
                time_str = text[len('/time'):].strip()
                return EventData(EventType.ADD_CRON_TRIGGER, chat_id, time_str)
            
            if text.lower().startswith('/add'):
                city_name = text[len('/add'):].strip()
                city_name = city_name.replace(' ', '_')  # TODO copypaste
                return EventData(EventType.ADD_CITY, chat_id, city_name)

            if text.startswith('/') and text[1:].strip().isdigit():
                number = int(text[1:].strip())
                return EventData(EventType.CHOOSE_CITY, chat_id, str(number - 1))

            if text.startswith('/') and len(text) > 2:  # city command
                city_name = text[1:].strip()
                city_name = city_name.replace(' ', '_')  # TODO copypaste
                if len(city_name) > 1:
                    return EventData(EventType.CITY, chat_id, city_name)
            
            if text.lower() == '/k':
                return EventData(EventType.CITY, chat_id, default_city_name)
    return EventData(EventType.OTHER, None, '')
    

def lambda_handler(event: dict, context) -> dict:
    event_data = parse_event(event)
    
    success = {'statusCode': 200, 'body': 'Success'}
    
    if event_data.type is EventType.OTHER:
        return success
    
    if event_data.type is EventType.SCHEDULED:
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
    
    # if event_data.type is EventType.ADD_CRON_TRIGGER:
    
    chat_id = event_data.chat_id
    
    if event_data.type is EventType.START:
        text = f'Здравствуйте! Бот показывает погоду в выбранном месте в данный момент (текстом) и прогнозом на несколько дней (картинкой).' \
                f' По кнопке Меню слева внизу есть список команд бота'
        tg_api_connector.send_message({chat_id}, text, None)
        return success
    
    if event_data.type is EventType.HERE:
        text = f'Можете нажать на кнопочку' \
                f' "{messages.BUTTON_WEATHER_HERE_TEXT}",' \
                f' если хотите посмотреть погоду там, где вы находитесь'
        tg_api_connector.send_message({chat_id}, text, None,
                                      want_user_location=True)
        return success
    
    chosen_city = None
    command_type = None
    if event_data.type is EventType.USER_LOCATION:
        location_str = event_data.info
        lat, lon = [float(x) for x in location_str.split(',')]
        city_options = list(weather_connector.get_city_options(lat=lat, lon=lon))
        
        if not city_options:
            text = f'Здравствуйте. Вот ищу я, ищу ... хоть убей, нет ни одного' \
                f' {event_data.info}. Странно это как-то ...'
            
            tg_api_connector.send_message({chat_id}, text, None)
            return success
        
        chosen_city = city_options[0]
        command_type = event_data.type
        event_data = EventData(EventType.CHOOSE_CITY, chat_id, '')
    
    elif event_data.type in (EventType.CITY, EventType.ADD_CITY):
        if not event_data.info:
            text = messages.EMPTY_ADD_TEXT
            tg_api_connector.send_message({chat_id}, text, None)
            return success
        
        elif event_data.info == 'city':
            text = messages.CITY_CITY_TEXT
            tg_api_connector.send_message({chat_id}, text, None)
            return success
        
        city_options = list(weather_connector.get_city_options(city_name=event_data.info))
        
        if not city_options:
            text = f'Здравствуйте. Вот ищу я, ищу ... хоть убей, нет ни одного' \
                f' {event_data.info}. Странно это как-то ...'
            
            tg_api_connector.send_message({chat_id}, text, None)
            return success

        if len(city_options) > 1:
            db_update_feedback = update_db(event_data, city_options)
            text = create_choice_message(city_options)
            tg_api_connector.send_message({chat_id}, text, None,
                    use_reply_keyboard=True)
            return success
        
        else:
            chosen_city = city_options[0]
            command_type = event_data.type
            event_data = EventData(EventType.CHOOSE_CITY, chat_id, '')
    
    if event_data.type is EventType.CHOOSE_CITY:
        if not chosen_city:
            city_num = int(event_data.info)
            command_type, city_options = base.load_command(chat_id)
            chosen_city = city_options[city_num] if 0 <= city_num < len(city_options) else None

        if not chosen_city:
            text = f'Добрый вечер, сударь. С вами говорит начальник отдела' \
                    f' чисел, меньших 11. Что-то я сижу, смотрю в монитор,' \
                    f' и никак у меня не получается найти город с номером {city_num + 1}.' \
                    f' Однако, у нашего отдела впереди вся ночь, я вызвал сотрудников' \
                    f' из отпусков. Однажды мы справимся! И сразу с вами свяжемся'
            
            tg_api_connector.send_message({chat_id}, text, None)
            return success

        if command_type in (EventType.CITY, EventType.USER_LOCATION):  
            chats = base.get_chats()
            dark_mode = chats.get(chat_id, {}).get('dark_mode', cfg.DEFAULT_DARKMODE)  
            text, image = create_message(chosen_city, dark_mode)
            tg_api_connector.send_message({chat_id}, text, image)

        elif command_type is EventType.ADD_CITY:        
            db_update_feedback = update_db(event_data, [chosen_city])

            city_name = chosen_city.local_name
            old_without_new_cities = db_update_feedback
            old_without_new_cities_names = [c.local_name for c in old_without_new_cities]
            
            text = f'Буду напоминать о {city_name} по утрам'
            if old_without_new_cities:
                text += '. A ещё о ' + ', '.join(old_without_new_cities_names)
            
            tg_api_connector.send_message({chat_id}, text, None)
        
        if command_type is not EventType.USER_LOCATION: 
            location_str = f'&latitude={chosen_city.lat}&longitude={chosen_city.lon}' \
                    f'&horizontal_accuracy=1500'
            tg_api_connector.send_message({chat_id}, None, None, location_str=location_str)

        return success
    
    
    elif event_data.type in (EventType.SWITCH_DARKMODE, EventType.CLEAR_CITIES):
        db_update_feedback = update_db(event_data)

    assert event_data.type in (EventType.CLEAR_CITIES, 
            EventType.LIST_CITIES, EventType.SHOW_CITIES, EventType.SWITCH_DARKMODE)

    if event_data.type is EventType.SWITCH_DARKMODE:
        dark_mode = db_update_feedback
        text = f'Теперь картинка будет {"тёмная" if dark_mode else "светлая"}'
        tg_api_connector.send_message({chat_id}, text, None)
        return success
    
    assert event_data.type in (EventType.CLEAR_CITIES, 
            EventType.LIST_CITIES, EventType.SHOW_CITIES)
    
    if event_data.type is EventType.CLEAR_CITIES:
        text = f'Напоминалки обо всех городах удалены'
        tg_api_connector.send_message({chat_id}, text, None)
        return success

    assert event_data.type in (EventType.LIST_CITIES, EventType.SHOW_CITIES)
    
    chats = base.get_chats()
    
    if event_data.type is EventType.LIST_CITIES:
        cities = chats.get(chat_id, {}).get('cities', [])
        if not cities:
            text = f'Вы просили напоминать о пустом множестве городов!' \
                    f' Будет сделано! 🫡'
        else:
            city_descriptions = [create_city_description(c) for c in cities]
            text = f'Кажется, вы просили напоминать о:\n\n' \
                    + ' \n\n'.join(city_descriptions) \
                    + '\n\nОх, всего-то не упомнишь ...'
        
        tg_api_connector.send_message({chat_id}, text, None)
        return success

    assert event_data.type is EventType.SHOW_CITIES
    
    dark_mode = chats.get(chat_id, {}).get('dark_mode', cfg.DEFAULT_DARKMODE)
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


def update_db(event_data: EventData, cities: list[City] = None) -> Any:
    if event_data.type is EventType.SWITCH_DARKMODE:
        feedback = base.switch_darkmode(event_data.chat_id)
    elif event_data.type is EventType.CLEAR_CITIES:
        feedback = base.clear_cities(event_data.chat_id)
    elif event_data.type is EventType.CHOOSE_CITY:
        feedback = base.add_city(event_data.chat_id, cities[0])  # TODO what if cities is None or empty
    elif event_data.type in (EventType.ADD_CITY, 
                             EventType.CITY, 
                             EventType.USER_LOCATION):
        feedback = base.save_command(event_data, cities)
    else:
        assert False
    return feedback


def create_city_description(city: City) -> str:
    p = city.population
        #    f' {"%d:, чел," % city.population if city.population else ""}' \
    return f'🏘 *{city.local_name}*' \
           f' {city.admin_subject},' \
           f' {city.country}.' \
           f'{" {:,} чел,".format(p) if p else ""}' \
           f' {city.asl}м н.у.м.' \
           f' {city.lat:.2f},'\
           f' {city.lon:.2f}'


def create_choice_message(city_options: list[City]) -> str:
    text = f'Пожалуйста, выберите город:\n\n'
            
    for i, city in enumerate(city_options):
        city_description = create_city_description(city)
        text += f'{i + 1}. {city_description}\n\n'
    return text

@cache
def create_message(city: City, dark_mode: bool) -> \
        tuple[str, Optional[io.BytesIO]]:

    weather_text = weather_connector.get_weather_text(city)
    weather_image = weather_connector.get_weather_image(city, dark_mode)

    not_found_start = f'{city.local_name}, говорите ... \n\n'

    if weather_text == '':
        text_body = random.choice(messages.NOT_FOUND_WEATHER_TEXTS)
        weather_text = not_found_start + text_body

    if weather_image is None:
        if not weather_text.startswith(not_found_start):
            weather_text += messages.NOT_FOUND_WEATHER_IMAGE_TEXT

    return weather_text, weather_image


# if __name__ == '__main__':
#     getUpdates(timeout=30)


if __name__ == '__main__':
    for event in tests.events:
        lambda_handler(event, None)

    # for k, v in tests.__dict__.items():
    #     if k.startswith('test_') and isinstance(v, dict):
    #         lambda_handler(v, None)