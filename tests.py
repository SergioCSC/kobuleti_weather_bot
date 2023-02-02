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

commands = [
    '/clear',
    '/dark',
    '/list',
    '/show',
    '/add Вышний Волочёк',
    '/add Кобулети',
    '/New-York',
    '/add Вышний Волочёк',
    '/list',
    '/show',
    '/мухосранск',
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

for command in commands:

    body_start = '{\"update_id\":124257435,\n\"message\":{\"message_id\":439,\"from\":{\"id\":534111842,\"is_bot\":false,\"first_name\":\"Sergio\",\"username\":\"n_log_n\",\"language_code\":\"en\"},\"chat\":{\"id\":534111842,\"title\":\"Test Group for bots\",\"type\":\"supergroup\"},\"date\":1674068886,\"text\":\"'
    body_finish = '\",\"entities\":[{\"offset\":0,\"length\":2,\"type\":\"bot_command\"}]}}'

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
        "body": f'{body_start}{command}{body_finish}',
        "isBase64Encoded": "False"
    }
    events.append(event)