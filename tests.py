test_event_bridge = {
        "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "123456789012",
        "time": "1970-01-01T00:00:00Z",
        "region": "us-east-1",
        "resources": ["arn:aws:events:us-east-1:123456789012:rule/ExampleRule"],
        "detail": {},
    }

chat_id = 534111842
# chat_id = -1001899507998  # test group for bots
commands = [
    # 'Here',
    '/start',
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

# location_body = '{\"update_id\": \"124258214\", \"message\": {\"message_id\": \"2054\", \"from\": {\"id\": \"534111842\", \"is_bot\": \"False\", \"first_name\": \"Sergio\", \"username\": \"n_log_n\", \"language_code\": \"en\"}, \"chat\": {\"id\": \"534111842\", \"first_name\": \"Sergio\", \"username\": \"n_log_n\", \"type\": \"private\"}, \"date\": \"1675482937\", \"reply_to_message\": {\"message_id\": \"2052\", \"from\": {\"id\": \"5887622494\", \"is_bot\": \"True\", \"first_name\": \"kobuleti_weather\", \"username\": \"kobuleti_weather_bot\"}, \"chat\": {\"id\": \"534111842\", \"first_name\": \"Sergio\", \"username\": \"n_log_n\", \"type\": \"private\"}, \"date\": \"1675482838\", \"text\": \"Можете нажать на кнопочку Погода прямо тут, если хотите посмотреть погоду там, где вы находитесь\"}, \"location\": {\"latitude\": \"41.813107\", \"longitude\": \"41.782663\"}}}'

for command in commands:

    body_start = '{\"update_id\":124257435,\n\"message\":{\"message_id\":439,\"from\":{\"id\":534111842,\"is_bot\":false,\"first_name\":\"Sergio\",\"username\":\"n_log_n\",\"language_code\":\"en\"},\"chat\":{\"id\":'
    body_middle = ',\"title\":\"Test Group for bots\",\"type\":\"supergroup\"},\"date\":1674068886,\"text\":\"'
    body_finish = '\",\"entities\":[{\"offset\":0,\"length\":2,\"type\":\"bot_command\"}]}}'

    body = f'{body_start}{chat_id}{body_middle}{command}{body_finish}'
    # body = location_body
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