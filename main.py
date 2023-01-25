import base
import weather_connector
import tg_api_connector

import io
import json
import tests


def get_chat_set(event: dict) -> set[int]:
    if event.get('detail-type') == 'Scheduled Event':  # event initiated by Event Bridge
        return base.get_chat_set()
    elif event.get('httpMethod') in (
        'GET',
        'POST',
    ):  # event initiated by http api gateway
        update = event.get('body')
        assert update
        print(update)
        update = json.loads(update)
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
                return {chat_id}
        assert False
    else:
        assert False


def lambda_handler(event: dict, context) -> dict:
    city_name: str = 'Komsomolsk-on-Amur'  # TODO get_city(event)
    city_name: str = 'Москва'  # TODO get_city(event)
    weather = weather_connector.http_get_weather(city_name)
    message = weather_connector.create_weather_message(weather)

    chat_set = get_chat_set(event)
    image: io.BytesIO = weather_connector.get_weather_image(city_name)
    tg_api_connector.send_message(chat_set, message, image)
    return {'statusCode': 200, 'body': 'Success'}


if __name__ == '__main__':
    for k, v in tests.__dict__.items():
        if k.startswith('test_') and isinstance(v, dict):
            lambda_handler(v, None)