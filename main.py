import base

import json
import urllib
import tg_api_connector


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
    
    WEATHER_SITE = 'https://api.openweathermap.org/data/2.5/weather?lat=41.8141&lon=41.7739&units=metric&lang=ru&appid=11c0d3dc6093f7442898ee49d2430d20'
    message = tg_api_connector.get(WEATHER_SITE)
    d = json.load(message)
    celsius = float(d['main']['temp'])  # - 273.15
    pressure_mm_hg = int(float(d['main']['pressure']) * 3 / 4)
    humidity = int(d['main']['humidity'])
    wind_speed = float(d['wind']['speed'])
    weather_main = d['weather'][0]['main']
    weather_description = d['weather'][0]['description']
    # weather_icon = d['weather'][0]['icon']
    
    weather_icon = ''
    if weather_main == 'Clear':
        weather_icon = '🌞'
    
    message = (
        f'❣️ Кобулети\n'
        f'🌡 {celsius:.0f} °C, {weather_icon} {weather_description}\n'
        f'ветер 💨 {wind_speed:.0f} м/с\n'
        f'влажность 🚰 {humidity}%\n'
        f'давление 🎈 {pressure_mm_hg} мм рт. ст.'
    )
    message = urllib.parse.quote(message.encode('utf-8'))
    
    chat_set = get_chat_set(event)
    tg_api_connector.send_message(chat_set, message)
    
    return {'statusCode': 200, 'body': 'Success'}



def test_event_bridge_run():
    test_event = {
        "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "123456789012",
        "time": "1970-01-01T00:00:00Z",
        "region": "us-east-1",
        "resources": ["arn:aws:events:us-east-1:123456789012:rule/ExampleRule"],
        "detail": {},
    }

    lambda_handler(test_event, None)


def http_request_from_tg_test_run():
    test_event = {
        "version": "1.0",
        "resource": "/kobuleti_weather",
        "path": "/default/kobuleti_weather",
        "httpMethod": "POST",
        "headers": {
            "Content-Length": "323",
            "Content-Type": "application/json",
            "Host": "1ykm8geil9.execute-api.us-east-1.amazonaws.com",
            "X-Amzn-Trace-Id": "Root=1-63c84418-1cdec56523ada7094cd8702d",
            "X-Forwarded-For": "91.108.6.97",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https",
            "accept-encoding": "gzip, deflate",
        },
        "multiValueHeaders": {
            "Content-Length": ["323"],
            "Content-Type": ["application/json"],
            "Host": ["1ykm8geil9.execute-api.us-east-1.amazonaws.com"],
            "X-Amzn-Trace-Id": ["Root=1-63c84418-1cdec56523ada7094cd8702d"],
            "X-Forwarded-For": ["91.108.6.97"],
            "X-Forwarded-Port": ["443"],
            "X-Forwarded-Proto": ["https"],
            "accept-encoding": ["gzip, deflate"],
        },
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "requestContext": {
            "accountId": "145384694416",
            "apiId": "1ykm8geil9",
            "domainName": "1ykm8geil9.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "1ykm8geil9",
            "extendedRequestId": "e8-T6jzPIAMEVrw=",
            "httpMethod": "POST",
            "identity": {
                "accessKey": None,
                "accountId": None,
                "caller": None,
                "cognitoAmr": None,
                "cognitoAuthenticationProvider": None,
                "cognitoAuthenticationType": None,
                "cognitoIdentityId": None,
                "cognitoIdentityPoolId": None,
                "principalOrgId": None,
                "sourceIp": "91.108.6.97",
                "user": None,
                "userAgent": "",
                "userArn": None,
            },
            "path": "/default/kobuleti_weather",
            "protocol": "HTTP/1.1",
            "requestId": "e8-T6jzPIAMEVrw=",
            "requestTime": "18/Jan/2023:19:10:16 +0000",
            "requestTimeEpoch": 1674069016865,
            "resourceId": "ANY /kobuleti_weather",
            "resourcePath": "/kobuleti_weather",
            "stage": "default",
        },
        "pathParameters": None,
        "stageVariables": None,
        "body": '{"update_id":124257435,\n"message":{"message_id":439,"from":{"id":534111842,"is_bot":false,"first_name":"Sergio","username":"n_log_n","language_code":"en"},"chat":{"id":-1001899507998,"title":"Test Group for bots","type":"supergroup"},"date":1674068886,"text":"/s","entities":[{"offset":0,"length":2,"type":"bot_command"}]}}',
        "isBase64Encoded": False,
    }

    lambda_handler(test_event, None)


if __name__ == '__main__':
    test_event_bridge_run()
    http_request_from_tg_test_run()