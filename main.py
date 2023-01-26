import config as cfg
import base
import weather_connector
import tg_api_connector

import io
import json
import tests

        
def get_city_and_chats(event) -> tuple[str, set[int]]:
    default_city_name = cfg.DEFAULT_CITY
    if event.get('detail-type') == 'Scheduled Event':  # event initiated by Event Bridge
        return default_city_name, base.get_chat_set()  # TODO
    elif event.get('httpMethod') in (
        'GET',
        'POST',
    ):  # event initiated by http api gateway
        update = event.get('body')
        assert update
        update = json.loads(update)
        print(f'{update = }')
        for key in (
            'message',
            'edited_message',
            'channel_post',
            'edited_channel_post',
            'chat_member',
            'my_chat_member',
            'chat_join_request',
        ):
            if key in update:
                chat_id = int(update[key]['chat']['id'])
                base.add_chat(chat_id)
                # message_type = update[key].get('entities',[{}])[0].get('type')
                
                text = update[key].get('text', '')
                text = bytes(text, 'utf-8').decode('utf-8')
                if text.startswith('/'):  # command
                    text = text[1:]
                    if len(text) > 1:  # city command
                        # base.add_???(???) TODO
                        return text, {chat_id}
                return default_city_name, {chat_id}
    
    assert False  # TODO raise


def lambda_handler(event: dict, context) -> dict:
    city_name, chat_set = get_city_and_chats(event)
    print(f'{city_name = }')
    try:
        weather = weather_connector.http_get_weather(city_name)
        message = weather_connector.create_weather_message(weather)
    except Exception as e:
        print(f'Exception in weather_connector.http_get_weather({city_name})')
        message = f'Чёт я не нашла {city_name} на {cfg.OPENWEATHERMAP_SITE}' \
                f' Галя! Гааа-ляяя! Слушай, ты слышала про такой город, {city_name}?' \
                f' C кем ты туда ездила? А, ну так я и думала.' \
                f'\n\nВ общем, извините, такого города не существует'
    try:
        image: io.BytesIO = weather_connector.get_weather_image(city_name)
    except Exception as e:
        print(f'Exception in weather_connector.get_weather_image({city_name})')
        image = None
        if not message.startswith('Чёт я не нашла'):
            message += '\n\nМожно ваш паспорт? Спасибо. Таааак ...' \
                ' Галя, не видишь, я занята. Что там у вас  ... аааа, ну конечно!' \
                ' А вы вообще в курсе, что вам никакие графики никаких температур не положены?' \
                ' Да, совсем. Не задерживайте очередь.' \
                ' Если вам так надо,' \
                ' подходите завтра к 8 утра в регистратуру с анализами.' \
                ' За результатами через 60 рабочих дней. Что вам ещё?' \
                ' Нет, через госуслуги нельзя. До свидания.\n\nИшь, прогноз погоды им подавай'
    tg_api_connector.send_message(chat_set, message, image)
    return {'statusCode': 200, 'body': 'Success'}


if __name__ == '__main__':
    for k, v in tests.__dict__.items():
        if k.startswith('test_') and isinstance(v, dict):
            lambda_handler(v, None)