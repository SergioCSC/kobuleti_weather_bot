test_event_bridge = {
        "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "123456789012",
        "time": "1970-01-01T00:00:00Z",
        "region": "us-east-1",
        "resources": ["arn:aws:events:us-east-1:123456789012:rule/ts_1676146104_23_10_chat_-1001899507998"],
        "detail": {},
    }

# chat_id = 534111842
chat_id = -1001899507998  # test group for bots
commands = [
    '/петрпавловск камчатский',
    # '/лондон',
    # '/home clear',
    # '/time',
    # '/time 4.4',
    # '/home спб',
    # '/time 19.19 20.20',
    # '/шли ничего',
    # '/time 4.3',
    # '/time 4.6',
    # '/time 13.16',
    # '/time',
    # '/time 4.4 вс',
    # '/time 4.3 вс',
    # '/time 4.5 вс',
    # '/time 6.5 пн',
    # '/time 7.4 пн',
    # '/time 5.6 пн',
    # '/time 5.5 чт',
    # '/time 5.4 чт',
    # '/time 5.6 чт',
    # '/time 13.15 чт',
    # '/time 13.20 чт',
    # '/time 13.10 чт',
    # '/time 13.05 чт',
    # '/time 13.25 чт',
    # '/time',
    # '/time clear',
    # '/time сб 9.45',
    # 'Here',
    # '/start',
    # '/сосновка',
    # '/5',
    # '/спб',
    # '/add Кобулети',
    # '/1',
    # '/мухосранск',
    # '/add мухосранск',
    # '/0',
    # '/clear',
    # '/dark',
    # '/list',
    # '/show',
    # '/воркута',
    # '/1',
    # '/add Вышний Волочёк',
    # '/1',
    # '/снежинск',
    # '/1',
    # '/2',
    # '/list',
    # '/add Кобулети',
    # '/New-York',
    # '/add Вышний Волочёк',
    # '/add буй',
    # '/add сибирка',
    # '/add мариинск',
    # '/add павлово',
    # '/list',
    # '/show',
    # '/мухосранск',
    # '/add Нарофоминск@kobuleti_weather_bot',
    # '/ @kobuleti_weather_bot',
    # '/add@kobuleti_weather_bot',
    # '/@kobuleti_weather_bot',
    # '/dark',
    # '/s',
    # '/k@kobuleti_weather_bot',
    # '/магнитогорск',
    # '/Санкт-Петербург',
    # '/мухосранск',
]

# events = [test_event_bridge]
events = []

location_body = '{\"update_id\": \"124258214\", \"message\": {\"message_id\": \"2054\", \"from\": {\"id\": \"534111842\", \"is_bot\": \"False\", \"first_name\": \"Sergio\", \"username\": \"n_log_n\", \"language_code\": \"en\"}, \"chat\": {\"id\": \"534111842\", \"first_name\": \"Sergio\", \"username\": \"n_log_n\", \"type\": \"private\"}, \"date\": \"1675482937\", \"reply_to_message\": {\"message_id\": \"2052\", \"from\": {\"id\": \"5887622494\", \"is_bot\": \"True\", \"first_name\": \"kobuleti_weather\", \"username\": \"kobuleti_weather_bot\"}, \"chat\": {\"id\": \"534111842\", \"first_name\": \"Sergio\", \"username\": \"n_log_n\", \"type\": \"private\"}, \"date\": \"1675482838\", \"text\": \"Можете нажать на кнопочку Погода прямо тут, если хотите посмотреть погоду там, где вы находитесь\"}, \"location\": {\"latitude\": \"41.813107\", \"longitude\": \"41.782663\"}}}'
reply_to_reply_body = '{\"update_id\": 124259004, \"message\": {\"message_id\": 2214, \"from\": {\"id\": 534111842, \"is_bot\": \"False\", \"first_name\": \"Sergio\", \"username\": \"n_log_n\", \"language_code\": \"en\"}, \"chat\": {\"id\": -1001899507998, \"title\": \"Test Group for bots\", \"type\": \"supergroup\"}, \"date\": 1676275053, \"message_thread_id\": 2210, \"reply_to_message\": {\"message_id\": 2211, \"from\": {\"id\": 534111842, \"is_bot\": \"False\", \"first_name\": \"Sergio\", \"username\": \"n_log_n\", \"language_code\": \"en\"}, \"chat\": {\"id\": -1001899507998, \"title\": \"Test Group for bots\", \"type\": \"supergroup\"}, \"date\": 1676275038, \"message_thread_id\": 2210, \"text\": \"1\"}, \"text\": \"reply на город\"}}'
for command in commands:

    body_start = '{\"update_id\":124257435,\n\"message\":{\"message_id\":439,\"from\":{\"id\":534111842,\"is_bot\":false,\"first_name\":\"Sergio\",\"username\":\"n_log_n\",\"language_code\":\"en\"},\"chat\":{\"id\":'
    body_middle = ',\"title\":\"Test Group for bots\",\"type\":\"supergroup\"},\"date\":1674068886,\"text\":\"'
    body_finish = '\",\"entities\":[{\"offset\":0,\"length\":2,\"type\":\"bot_command\"}]}}'

    body = f'{body_start}{chat_id}{body_middle}{command}{body_finish}'
    # body = location_body
    body = reply_to_reply_body
    event = {
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
            "accept-encoding": "gzip, deflate"
        },
        "multiValueHeaders": {
            "Content-Length": ["323"],
            "Content-Type": ["application/json"],
            "Host": ["1ykm8geil9.execute-api.us-east-1.amazonaws.com"],
            "X-Amzn-Trace-Id": ["Root=1-63c84418-1cdec56523ada7094cd8702d"],
            "X-Forwarded-For": ["91.108.6.97"],
            "X-Forwarded-Port": ["443"],
            "X-Forwarded-Proto": ["https"],
            "accept-encoding": ["gzip, deflate"]
        },
        "queryStringParameters": "None",
        "multiValueQueryStringParameters": "None",
        "requestContext": {
            "accountId": "145384694416",
            "apiId": "1ykm8geil9",
            "domainName": "1ykm8geil9.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "1ykm8geil9",
            "extendedRequestId": "e8-T6jzPIAMEVrw=",
            "httpMethod": "POST",
            "identity": {
                "accessKey": "None",
                "accountId": "None",
                "caller": "None",
                "cognitoAmr": "None",
                "cognitoAuthenticationProvider": "None",
                "cognitoAuthenticationType": "None",
                "cognitoIdentityId": "None",
                "cognitoIdentityPoolId": "None",
                "principalOrgId": "None",
                "sourceIp": "91.108.6.97",
                "user": "None",
                "userAgent": "",
                "userArn": "None"
            },
            "path": "/default/kobuleti_weather",
            "protocol": "HTTP/1.1",
            "requestId": "e8-T6jzPIAMEVrw=",
            "requestTime": "18/Jan/2023:19:10:16 +0000",
            "requestTimeEpoch": 1674069016865,
            "resourceId": "ANY /kobuleti_weather",
            "resourcePath": "/kobuleti_weather",
            "stage": "default"
        },
        "pathParameters": "None",
        "stageVariables": "None",
        "body": body,
        "isBase64Encoded": "False"
    }
    events.append(event)

from typing import NamedTuple, Any

class LambdaContext(NamedTuple):
    aws_request_id: str
    log_group_name: str
    log_stream_name: str
    function_name: str
    memory_limit_in_mb: int
    function_version: str
    invoked_function_arn: str
    client_context: Any
    identity: Any
    
    
context = LambdaContext(
        aws_request_id='654f275b-f673-46ab-a0f3-2c12f70b7b09',
        log_group_name='/aws/lambda/kobuleti_weather',
        log_stream_name='2023/02/08/[$LATEST]e6f6d4ae7ab049248cf4122ce9a57197',
        function_name='kobuleti_weather',
        memory_limit_in_mb=128,
        function_version='$LATEST',
        invoked_function_arn='arn:aws:lambda:us-east-1:145384694416:function:kobuleti_weather',
        client_context=None,
        identity=None)