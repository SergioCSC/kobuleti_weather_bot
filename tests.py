# test_event_bridge = {
#         "id": "cdc73f9d-aea9-11e3-9d5a-835b769c0d9c",
#         "detail-type": "Scheduled Event",
#         "source": "aws.events",
#         "account": "123456789012",
#         "time": "1970-01-01T00:00:00Z",
#         "region": "us-east-1",
#         "resources": ["arn:aws:events:us-east-1:123456789012:rule/ExampleRule"],
#         "detail": {},
#     }

add_command_body = "{\"update_id\":124257435,\n\"message\":{\"message_id\":439,\"from\":{\"id\":534111842,\"is_bot\":false,\"first_name\":\"Sergio\",\"username\":\"n_log_n\",\"language_code\":\"en\"},\"chat\":{\"id\":534111842,\"title\":\"Test Group for bots\",\"type\":\"supergroup\"},\"date\":1674068886,\"text\":\"/add@kobuleti_weather_bot\",\"entities\":[{\"offset\":0,\"length\":2,\"type\":\"bot_command\"}]}}"
switch_darkmode_command_body = "{\"update_id\":124257435,\n\"message\":{\"message_id\":439,\"from\":{\"id\":534111842,\"is_bot\":false,\"first_name\":\"Sergio\",\"username\":\"n_log_n\",\"language_code\":\"en\"},\"chat\":{\"id\":534111842,\"title\":\"Test Group for bots\",\"type\":\"supergroup\"},\"date\":1674068886,\"text\":\"/dark\",\"entities\":[{\"offset\":0,\"length\":2,\"type\":\"bot_command\"}]}}"
short_command_body = "{\"update_id\":124257435,\n\"message\":{\"message_id\":439,\"from\":{\"id\":534111842,\"is_bot\":false,\"first_name\":\"Sergio\",\"username\":\"n_log_n\",\"language_code\":\"en\"},\"chat\":{\"id\":-1001899507998,\"title\":\"Test Group for bots\",\"type\":\"supergroup\"},\"date\":1674068886,\"text\":\"/s\",\"entities\":[{\"offset\":0,\"length\":2,\"type\":\"bot_command\"}]}}"
long_command_body = "{\"update_id\":124257435,\n\"message\":{\"message_id\":439,\"from\":{\"id\":534111842,\"is_bot\":false,\"first_name\":\"Sergio\",\"username\":\"n_log_n\",\"language_code\":\"en\"},\"chat\":{\"id\":-1001899507998,\"title\":\"Test Group for bots\",\"type\":\"supergroup\"},\"date\":1674068886,\"text\":\"/k@kobuleti_weather_bot\",\"entities\":[{\"offset\":0,\"length\":2,\"type\":\"bot_command\"}]}}"
magnitogorsk_command_body = "{\"update_id\":124257435,\n\"message\":{\"message_id\":439,\"from\":{\"id\":534111842,\"is_bot\":false,\"first_name\":\"Sergio\",\"username\":\"n_log_n\",\"language_code\":\"en\"},\"chat\":{\"id\":-1001899507998,\"title\":\"Test Group for bots\",\"type\":\"supergroup\"},\"date\":1674068886,\"text\":\"/магнитогорск\",\"entities\":[{\"offset\":0,\"length\":2,\"type\":\"bot_command\"}]}}"
petersburg_command_body = "{\"update_id\":124257435,\n\"message\":{\"message_id\":439,\"from\":{\"id\":534111842,\"is_bot\":false,\"first_name\":\"Sergio\",\"username\":\"n_log_n\",\"language_code\":\"en\"},\"chat\":{\"id\":-1001899507998,\"title\":\"Test Group for bots\",\"type\":\"supergroup\"},\"date\":1674068886,\"text\":\"/Санкт-Петербург\",\"entities\":[{\"offset\":0,\"length\":2,\"type\":\"bot_command\"}]}}"
muhin_command_body = "{\"update_id\":124257435,\n\"message\":{\"message_id\":439,\"from\":{\"id\":534111842,\"is_bot\":false,\"first_name\":\"Sergio\",\"username\":\"n_log_n\",\"language_code\":\"en\"},\"chat\":{\"id\":-1001899507998,\"title\":\"Test Group for bots\",\"type\":\"supergroup\"},\"date\":1674068886,\"text\":\"/мухосранск\",\"entities\":[{\"offset\":0,\"length\":2,\"type\":\"bot_command\"}]}}"

test_tg_short_command = {
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
        "body": short_command_body,
        "isBase64Encoded": "False"
    }

test_add_cities_command = test_tg_short_command.copy()
test_add_cities_command['body'] = add_command_body

test_long_command = test_tg_short_command.copy()
test_long_command['body'] = long_command_body

test_magnitogorsk_command = test_tg_short_command.copy()
test_magnitogorsk_command['body'] = magnitogorsk_command_body

test_tg_petersburg_command = test_tg_short_command.copy()
test_tg_petersburg_command['body'] = petersburg_command_body

test_tg_muhin_command = test_tg_short_command.copy()
test_tg_muhin_command['body'] = muhin_command_body

test_switch_dark_mode_command = test_tg_short_command.copy()
test_switch_dark_mode_command['body'] = switch_darkmode_command_body