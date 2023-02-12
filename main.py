import config as cfg
import utils
from city import City
import base
import weather_connector
import tg_api_connector
from event import EventType, EventData
import messages
import aws_trigger

import io
import json
import tests
import random
import requests
import traceback
from typing import Any, Optional
from functools import cache


def parse_event(event) -> EventData:
    default_city_name = cfg.DEFAULT_CITY
    if event.get('detail-type') == 'Scheduled Event':  # event initiated by Event Bridge
        chat_id_str = event.get('resources')[0].split('/')[1].split('_')[-1]
        chat_id = int(chat_id_str) if chat_id_str.lstrip('-').isdigit() else None
        return EventData(EventType.SCHEDULED, chat_id, '')
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
                if not location:
                    return EventData(EventType.OTHER, None, '')
                else:
                    latitude = location['latitude']
                    longitude = location['longitude']
                    location_str = f'{latitude},{longitude}'
                    return EventData(EventType.USER_LOCATION, chat_id, 
                                     location_str)
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
            
            if text.lower().startswith('/time') or text.lower().startswith('/буди'):
                if text.lower().startswith('/time'):
                    time_str = text[len('/time'):].strip()
                else:
                    time_str = text[len('/буди'):].strip()

                if not time_str:
                    return EventData(EventType.LIST_CRON_TRIGGERS, chat_id, '')
                if time_str == 'clear' or time_str == 'никогда':
                    return EventData(EventType.CLEAR_CRON_TRIGGERS, chat_id, '')
                else:
                    return EventData(EventType.ADD_CRON_TRIGGER, chat_id, time_str)
            
            if text.lower().startswith('/add'):
                city_name = text[len('/add'):].strip()
                city_name = city_name.replace(' ', '_')  # TODO copypaste
                return EventData(EventType.ADD_CITY, chat_id, city_name)

            if text.lower().startswith('/home'):
                info = text[len('/home'):].strip()
                info = info.replace(' ', '_')  # TODO copypaste
                return EventData(EventType.HOME_CITY, chat_id, info)

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
    try:
        return _lambda_handler(event, context)
    except Exception as e:
        utils.print_with_time(f'Exception: {e = }\n\n')
        utils.print_with_time(f'Traceback: {traceback.print_exc() = }\n\n')
        return cfg.LAMBDA_SUCCESS


def _lambda_handler(event: dict, context) -> dict:
    event_data = parse_event(event)
    
    if event_data.type is EventType.OTHER:
        return cfg.LAMBDA_SUCCESS
    
    chat_id = event_data.chat_id
    
    if event_data.type is EventType.SCHEDULED:
        chats = base.get_chats()
        
        chat_ids = [chat_id] if chat_id else chats.keys()
        
        for chat_id in chat_ids:
            # if chat_id not in (534111842, -1001899507998):
            #     return cfg.LAMBDA_SUCCESS
            
            chat_info = chats.get(chat_id, {})  

            dark_mode = chat_info.get('dark_mode', cfg.DEFAULT_DARKMODE)
            cities = chat_info.get('cities', [])
            for city in cities:
                city_name = city.local_name            
                text, image, _ = get_text_image_tz(city, dark_mode)
                tg_api_connector.send_message({chat_id}, text, image)
        return cfg.LAMBDA_SUCCESS

    if event_data.type is EventType.START:
        text = f'Здравствуйте! Бот показывает погоду в выбранном месте в данный момент (текстом) и прогнозом на несколько дней (картинкой).' \
                f' По кнопке Меню слева внизу есть список команд бота'
        tg_api_connector.send_message({chat_id}, text, None)
        return cfg.LAMBDA_SUCCESS
    
    if event_data.type is EventType.ADD_CRON_TRIGGER:
        chat_timezone = get_chat_timezone(chat_id)
        if not chat_timezone:
            return cfg.LAMBDA_SUCCESS

        time_str = event_data.info

        time_of_day, weekday = aws_trigger.make_aws_trigger(
                chat_id, time_str, chat_timezone, context)
    
        if not time_of_day:
            text = f'Добрый день! Ваш паспорт и снилс! Вы по какому вопросу? Будильника?' \
                    f' Вам на 17-й этаж, кабинет справа по коридору.' \
                    f' Куда же вы пошли? Лифт только для персонала, вам туда ... Подождите, куда же вы опять?' \
                    f' Купите бахилы и маску, пожалуйста ... Кстати, дайте-ка сюда вашу анкету.' \
                    f' Ну конечно! У вас ошибка. Вместо {"/time " + time_str} надо написать либо\n\n' \
                    f'/time\n\nили\n\n/буди\n\n' \
                    f'-- это будет значить, что вы хотите посмотреть список всех будильников. Либо\n\n' \
                    f'/time clear\n\nили\n\n/буди никогда\n\n' \
                    f'-- это будет значить, что вы хотите удалить все будильники. Либо\n\n' \
                    f'/time 9\n\nили\n\n/time 9.30\n\nили\n\n/time пн 9.30\n\nили\n\n' \
                    f'/буди 9\n\nили\n\n/буди 9.30\n\nили\n\n/буди пн 9.30\n\n' \
                    f'-- поставить будильник на каждый день на 9 или 9.30, либо только по понедельникам в 9.30\n\n' \
                    f'У нас с бумагами строго. Ладно, идите. Эй, постойте! Куда вы!\n\nНе слышит. Ладно, сбегает в регистратуру, оно полезно'
            tg_api_connector.send_message({chat_id}, text, None)
            return cfg.LAMBDA_SUCCESS
    
        chats = base.get_chats()
        cities = chats.get(chat_id, {}).get('cities', [])
        city_names = [c.local_name for c in cities]
        cities_text = ', '.join(city_names)
        text = f'Буду напоминать о городах {cities_text} в:\n\n' \
                f'{aws_trigger.time_2_str(time_of_day, weekday)}'
        tg_api_connector.send_message({chat_id}, text, None)
        return cfg.LAMBDA_SUCCESS
    
    if event_data.type is EventType.LIST_CRON_TRIGGERS:
        timezone = get_chat_timezone(chat_id)
        if not timezone:
            return cfg.LAMBDA_SUCCESS
        
        time_shift = aws_trigger.TimeOfDay(+timezone.hours, +timezone.minutes)
        
        triggers = aws_trigger.get_aws_triggers(chat_id, context)
        
        times = []
        for trigger in triggers:
            splitted_trigger = trigger.split('_')
            weekday_str = splitted_trigger[2]
            weekdays = [d for d in aws_trigger.Weekday if d.name == weekday_str]
            if weekdays:
                weekday = weekdays[0]
                hours = int(splitted_trigger[3])
                minutes = int(splitted_trigger[4])
            else:
                weekday = None
                hours = int(splitted_trigger[2])
                minutes = int(splitted_trigger[3])
            
            time_of_day = aws_trigger.TimeOfDay(hours, minutes)
            shifted_time_of_day, shifted_weekday = aws_trigger._add_time_shift(time_of_day, weekday, time_shift)

            # time_str = aws_trigger.time_2_str(aws_trigger.TimeOfDay(hours, minutes), weekday)
            times.append((shifted_time_of_day, shifted_weekday))

        image = None
        times.sort(key=lambda d: (8 if d[1] is aws_trigger.Weekday.SUNDAY else d[1].value, d[0]) if d[1] else (-1, d[0]))
        times = [aws_trigger.time_2_str(*t) for t in times]
        if not times:
            times = ['Ой, всё, не буду напоминать']
        chats = base.get_chats()
        cities = chats.get(chat_id, {}).get('cities', [])
        city_names = [c.local_name for c in cities]
        cities_text = ', '.join(city_names)
        text = f'Буду напоминать о городах {cities_text} в:\n\n' + '\n'.join(times)
        tg_api_connector.send_message({chat_id}, text, image)
        return cfg.LAMBDA_SUCCESS

    if event_data.type is EventType.CLEAR_CRON_TRIGGERS:
        aws_trigger.clear_aws_triggers(chat_id, context)
        text = 'Фух, хорошо, больше никаких рутинных напоминалок!' \
                f' Раз такое дело, вечерком разберу и почищу любимый морской хронометр ...'
        picture_url = 'https://memepedia.ru/wp-content/uploads/2019/08/nu-da-nu-da-poshel-ya-na-her.jpg'
        response = requests.get(picture_url)
        image = io.BytesIO(response.content)
        tg_api_connector.send_message({chat_id}, text, image)
        return cfg.LAMBDA_SUCCESS

    if event_data.type is EventType.HERE:
        text = f'Можете нажать на кнопочку' \
                f' "{messages.BUTTON_WEATHER_HERE_TEXT}",' \
                f' если хотите посмотреть погоду там, где вы находитесь'
                # f' А если вы сидите не с телефона или просто не хотите делиться' \
                # f' своим местоположением, то введите город'
        tg_api_connector.send_message({chat_id}, text, None,
                                      want_user_location=True)
        return cfg.LAMBDA_SUCCESS
    
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
            return cfg.LAMBDA_SUCCESS

        chosen_city = city_options[0]
        command_type = event_data.type
        event_data = EventData(EventType.CHOOSE_CITY, chat_id, '')
    
    elif event_data.type in (EventType.CITY, EventType.ADD_CITY, EventType.HOME_CITY):
        if not event_data.info:
            if event_data.type is EventType.HOME_CITY:
                chat_city = base.load_chat_city(chat_id)
                if chat_city:
                    text = create_city_description(chat_city)
                else:
                    text = 'Ой, простите ... у нас тут записано, что вы нигде не живёте. ' \
                            f' Галя! Гааа-ляяя! Простите ... Извините ... Сейчас ...' \
                            f' Напишите пока, пожалуйста, ваш город, вот так:\n\n' \
                            f'/home Екатеринбург\n\n' \
                            f'А Галя сейчас допьёт кофе и запишет вас'
                tg_api_connector.send_message({chat_id}, text, None)
                return cfg.LAMBDA_SUCCESS
            command = event_data.type.name.lower().split('_')[0]
            text = messages.EMPTY_ADD_TEXT % (command, command)
            tg_api_connector.send_message({chat_id}, text, None)
            return cfg.LAMBDA_SUCCESS
        
        elif event_data.info == 'clear' \
                and event_data.type is EventType.HOME_CITY:
            base.clear_chat_city(chat_id)
            text = 'Гааа-ляяяя! Забудь пожалуйста, где живёт этот гражданин!\n\n' \
                    f'База данных очищена, сударь'
            tg_api_connector.send_message({chat_id}, text, None)
            return cfg.LAMBDA_SUCCESS
        
        elif event_data.info == 'city':
            text = messages.CITY_CITY_TEXT
            tg_api_connector.send_message({chat_id}, text, None)
            return cfg.LAMBDA_SUCCESS
        
        city_options = list(weather_connector.get_city_options(city_name=event_data.info))
        
        if not city_options:
            text = f'Здравствуйте. Вот ищу я, ищу ... хоть убей, нет ни одного' \
                f' {event_data.info}. Странно это как-то ...'
            
            tg_api_connector.send_message({chat_id}, text, None)
            return cfg.LAMBDA_SUCCESS

        if len(city_options) > 1:
            db_update_feedback = update_db(event_data, city_options)
            text = create_choice_message(city_options)
            tg_api_connector.send_message({chat_id}, text, None,
                    use_reply_keyboard=True)
            return cfg.LAMBDA_SUCCESS
        
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
            return cfg.LAMBDA_SUCCESS

        if command_type in (EventType.HOME_CITY, EventType.CITY, EventType.USER_LOCATION):  
            chats = base.get_chats()
            dark_mode = chats.get(chat_id, {}).get('dark_mode', cfg.DEFAULT_DARKMODE)  
            text, image, tz = get_text_image_tz(chosen_city, dark_mode)
            if command_type in (EventType.HOME_CITY, EventType.USER_LOCATION):
                c = chosen_city
                chosen_city = City(
                        c.local_name, 
                        c.iso2, 
                        c.country, 
                        c.admin_subject,
                        c.lat, 
                        c.lon, 
                        c.asl, 
                        c.population, 
                        c.distance, 
                        tz,
                        c.url_suffix_for_sig)
                base.save_chat_city(chat_id, chosen_city)
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

        return cfg.LAMBDA_SUCCESS
    
    
    elif event_data.type in (EventType.SWITCH_DARKMODE, EventType.CLEAR_CITIES):
        db_update_feedback = update_db(event_data)

    assert event_data.type in (EventType.CLEAR_CITIES, 
            EventType.LIST_CITIES, EventType.SHOW_CITIES, EventType.SWITCH_DARKMODE)

    if event_data.type is EventType.SWITCH_DARKMODE:
        dark_mode = db_update_feedback
        text = f'Теперь картинка будет {"тёмная" if dark_mode else "светлая"}'
        tg_api_connector.send_message({chat_id}, text, None)
        return cfg.LAMBDA_SUCCESS
    
    assert event_data.type in (EventType.CLEAR_CITIES, 
            EventType.LIST_CITIES, EventType.SHOW_CITIES)
    
    if event_data.type is EventType.CLEAR_CITIES:
        text = f'Напоминалки обо всех городах удалены'
        tg_api_connector.send_message({chat_id}, text, None)
        return cfg.LAMBDA_SUCCESS

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
        return cfg.LAMBDA_SUCCESS

    assert event_data.type is EventType.SHOW_CITIES
    
    dark_mode = chats.get(chat_id, {}).get('dark_mode', cfg.DEFAULT_DARKMODE)
    cities = chats.get(chat_id, {}).get('cities', [])

    if not cities:
        text = 'Сейчас-сейчас ... бегу ... ой, а ни одного' \
                f' города-то вы и не заказывали ...'
                
        tg_api_connector.send_message({chat_id}, text, None)
        return cfg.LAMBDA_SUCCESS

    for city in cities:
        text, image, _ = get_text_image_tz(city, dark_mode)
        tg_api_connector.send_message({chat_id}, text, image)
    return cfg.LAMBDA_SUCCESS


def update_db(event_data: EventData, cities: list[City] = None) -> Any:
    if event_data.type is EventType.SWITCH_DARKMODE:
        feedback = base.switch_darkmode(event_data.chat_id)
    elif event_data.type is EventType.CLEAR_CITIES:
        feedback = base.clear_cities(event_data.chat_id)
    elif event_data.type is EventType.CHOOSE_CITY:
        feedback = base.add_city(event_data.chat_id, cities[0])  # TODO what if cities is None or empty
    elif event_data.type in (EventType.HOME_CITY,
                             EventType.ADD_CITY, 
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


def get_chat_timezone(chat_id: int) -> Optional[aws_trigger.TimeOfDay]:
    if not (chat_city := base.load_chat_city(chat_id)):
        if str(chat_id).startswith('-100'):  # if group chat
            text = f'Вы хотите установить время, но вы не говорите мне свой' \
                    f' часовой пояс. Пожалуйста, установите ваш домашний город командой /home'

            picture_url = 'https://www.meme-arsenal.com/memes/710dd6fb3af6cfec6b218229a9f22170.jpg'
            response = requests.get(picture_url)
            image_bytes = io.BytesIO(response.content)
            tg_api_connector.send_message({chat_id}, text, image_bytes)
            
        else:
            text = f'Вы хотите установить время, но вы не говорите мне свой' \
                    f' часовой пояс. Пожалуйста, посмотрите погоду в вашей локации,' \
                    f' а я посмотрю ваш часовой пояс. А потом попробуйте установить' \
                    f' время ещё раз. Либо установите ваш домашний город командой /home'

            picture_url = 'https://www.meme-arsenal.com/memes/710dd6fb3af6cfec6b218229a9f22170.jpg'
            response = requests.get(picture_url)
            image_bytes = io.BytesIO(response.content)
            tg_api_connector.send_message({chat_id}, text, image_bytes,
                                want_user_location=True)
        return None

    chat_timezone_str = chat_city.tz
    chat_timezone = aws_trigger._parse_time(chat_timezone_str)
    return chat_timezone


def create_choice_message(city_options: list[City]) -> str:
    text = f'Пожалуйста, выберите город:\n\n'
            
    for i, city in enumerate(city_options):
        city_description = create_city_description(city)
        text += f'{i + 1}. {city_description}\n\n'
    return text

@cache
def get_text_image_tz(city: City, dark_mode: bool) \
        -> tuple[str, Optional[io.BytesIO], str]:

    weather_text = weather_connector.get_weather_text(city)
    weather_image, tz = weather_connector.get_weather_image_and_tz(city, dark_mode)

    not_found_start = f'{city.local_name}, говорите ... \n\n'

    if weather_text == '':
        text_body = random.choice(messages.NOT_FOUND_WEATHER_TEXTS)
        weather_text = not_found_start + text_body

    if weather_image is None:
        if not weather_text.startswith(not_found_start):
            weather_text += messages.NOT_FOUND_WEATHER_IMAGE_TEXT

    return weather_text, weather_image, tz


# if __name__ == '__main__':
#     getUpdates(timeout=30)


if __name__ == '__main__':
    for event in tests.events:
        lambda_handler(event, tests.context)

    # for k, v in tests.__dict__.items():
    #     if k.startswith('test_') and isinstance(v, dict):
    #         lambda_handler(v, None)