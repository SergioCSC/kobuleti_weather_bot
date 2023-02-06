import config as cfg
from city import City
from event import EventData, EventType
import utils

import boto3
import botocore
from botocore.exceptions import ClientError

from typing import Any
from decimal import Decimal

TABLE_NAME = 'weather-bot-chats'
TABLE = None


def get_chats() -> dict[int, dict[str, Any]]:
    # return {534111842, 253766343, -1001899507998, -1001889227859, 899881657}
    #         me       , Leh      ,test_group_bots,      monastery, l}
        # items = {
        #     534111842:
        #         {'id': 534111842,
        #         'dark_mode': False,
        #         'cities' : [
        #             ['Кобулети', 'GE', 'Грузия', 'Аджария', Decimal('41.8214'), Decimal('41.7792'), 3, 18600, Decimal('144.1440'), 'Asia/Tbilisi', '%d0%9a%d0%be%d0%b1%d1%83%d0%bb%d0%b5%d1%82%d0%b8_%d0%93%d1%80%d1%83%d0%b7%d0%b8%d1%8f_613762'],
        #             ['Вышний Волочёк', 'RU', 'Россия', 'Тверская область', Decimal('57.5913'), Decimal('34.5645'), 159, 53800, Decimal('1849.6460'), 'Europe/Moscow', '%d0%92%d1%8b%d1%88%d0%bd%d0%b8%d0%b9-%d0%92%d0%be%d0%bb%d0%be%d1%87%d1%91%d0%ba_%d0%a0%d0%be%d1%81%d1%81%d0%b8%d1%8f_470252'],
        #             ]
        #         },
        #     -1001899507998:
        #         {'id': -1001899507998,
        #         'cities' : [
        #             ['Йорк', 'US', 'США', 'Небраска', Decimal('40.8681'), Decimal('-97.5920'), 488, 7864, Decimal('10004.1380'), 'America/Chicago', '%d0%99%d0%be%d1%80%d0%ba_%d0%a1%d0%a8%d0%90_5082331'],
        #             ['Вышний Волочёк', 'RU', 'Россия', 'Тверская область', Decimal('57.5913'), Decimal('34.5645'), 159, 53800, Decimal('1849.6460'), 'Europe/Moscow', '%d0%92%d1%8b%d1%88%d0%bd%d0%b8%d0%b9-%d0%92%d0%be%d0%bb%d0%be%d1%87%d1%91%d0%ba_%d0%a0%d0%be%d1%81%d1%81%d0%b8%d1%8f_470252'],
        #             ]
        #         },
        #     }
    response = TABLE.scan()
    chats = response['Items']
    chats = {chat['id']: chat for chat in chats}
    
    if not cfg.IN_AWS_LAMBDA:
        chats = {k: v for k, v in chats.items() if k in (534111842, -1001899507998)}
    
    for chat in chats.values():
        _chat_decimals_to_cities(chat)
    
    return chats


# def get_chat_with_params(chat_id: int) -> dict:
#     chats_with_params = get_chats_with_params()
#     return chats_with_params[chat_id]


def _get_chat(chat_id: int) -> dict[str, Any]:
    chats_with_params = get_chats()
    return chats_with_params.get(chat_id, {'id': chat_id})


def _put_chat(chat: dict) -> None:
    _chat_cities_to_decimals(chat)
    TABLE.put_item(Item=chat)


# def add_chat(chat_id: int) -> None:
#     chat = _get_chat(chat_id)
    
#     if not chat:
#         chat = {'id': chat_id}  # TODO Кобулети
#         _put_chat(chat)
    
#     utils.print_with_time(f'Chat {chat_id} added into the table')

    
def add_city(chat_id: int, new_city: City) -> list[str]:
    chat = _get_chat(chat_id)

    old_cities = chat.get('cities', [])
    if new_city not in old_cities:
        chat['cities'] = old_cities + [new_city]
        _put_chat(chat)
        
    utils.print_with_time(f'City {new_city} added to {chat_id} in the table')
    old_without_new_cities = [c for c in old_cities if c != new_city]
    return old_without_new_cities
    
    
def save_command(event_data: EventData, 
                 city_options: list[City]) -> None:
    
    chat_id = event_data.chat_id
    city_name = event_data.info
    command = event_data.type
    
    chat = _get_chat(chat_id)

    chat['last_command'] = str(command).split('.')[1]
    chat['last_command_city_name'] = city_name
    chat['last_command_city_options'] = city_options
    _put_chat(chat)
    utils.print_with_time(f'Command {command} from {chat_id} saved into the table')
    return


def load_command(chat_id: int) -> tuple[EventType, str, list[City]]:
    chat = _get_chat(chat_id)

    command_str = chat.get('last_command', '')
    command = EventType[command_str] if command_str else None
    city_name = chat.get('last_command_city_name', '')
    city_options = chat.get('last_command_city_options', [])
    
    chat.pop('last_command', None)
    chat.pop('last_command_city_name', None)
    chat.pop('last_command_city_options', None)
    
    _put_chat(chat)
    utils.print_with_time(f'Command {command} from {chat_id} loaded from the table')
    return  command, city_options
    
    
def clear_cities(chat_id: int) -> None:
    chat = _get_chat(chat_id)
    chat['cities'] = []
    _put_chat(chat)
    utils.print_with_time(f'All cities cleared for {chat_id} in the table')


def list_cities(chat_id: int) -> list[City]:
    chat = _get_chat(chat_id)
    cities = chat.get('cities', [])
    utils.print_with_time(f'List of cities for {chat_id}: {", ".join(cities)}')
    return cities


def switch_darkmode(chat_id: int) -> bool:
    chat = _get_chat(chat_id)
    dark_mode = chat.get('dark_mode', cfg.DEFAULT_DARKMODE)
    dark_mode = not dark_mode
    
    chat['dark_mode'] = dark_mode
    _put_chat(chat)
    utils.print_with_time(f'Item {chat_id} with {dark_mode = }' \
                            f' has been put into the table')
    return dark_mode


def _decimal_to_city(decimal_city) -> City:
    return City(
        decimal_city[0],  # local_name
        decimal_city[1],  # iso2
        decimal_city[2],  # country
        decimal_city[3],  # admin_subject
        float(decimal_city[4]),  # lat
        float(decimal_city[5]),  # lon
        int(decimal_city[6]),  # asl
        int(decimal_city[7]),  # population
        float(decimal_city[8]),  # distance
        decimal_city[9],  # tz
        decimal_city[10],  # url_suffix_for_sig
    )


def _chat_decimals_to_cities(chat: dict[str, Any]) -> None:
    for key in ('cities', 'last_command_city_options'):
        if key in chat:
            chat[key] = [_decimal_to_city(d) for d in chat[key]]


def _city_to_decimal(city: City) -> tuple:
    return (
        city.local_name, 
        city.iso2, 
        city.country, 
        city.admin_subject, 
        Decimal(f'{city.lat:.5f}'), 
        Decimal(f'{city.lon:.5f}'), 
        city.asl, 
        city.population, 
        Decimal(f'{city.distance:.5f}'), 
        city.tz, 
        city.url_suffix_for_sig,
    )


def _chat_cities_to_decimals(chat: dict) -> None:
    # item = json.loads(json.dumps(item), parse_float=Decimal)
    for key in ('cities', 'last_command_city_options'):
        if key in chat:
            chat[key] = [_city_to_decimal(c) for c in chat[key]]
    


def _init_table() -> 'boto3.resources.factory.dynamodb.Table':
    utils.print_with_time('START TABLE INITIALIZATION')
    dynamodb_client = boto3.client('dynamodb', region_name=cfg.AWS_REGION)
    dynamodb_resource = boto3.resource('dynamodb', region_name=cfg.AWS_REGION)
    
    table = dynamodb_resource.Table(TABLE_NAME)
    if _check_if_table_exists(table):
        utils.print_with_time('FINISH TABLE INITIALIZATION')
        return table
    
    table = _create_table(dynamodb_client, dynamodb_resource, TABLE_NAME)
    
    utils.print_with_time('FINISH TABLE INITIALIZATION')
    return table


def _check_if_table_exists(table: 'boto3.resources.factory.dynamodb.Table') -> bool:
    try:
        table.load()
        exists = True
    except ClientError as err:
        if err.response['Error']['Code'] == 'ResourceNotFoundException':
            exists = False
        else:
            utils.print_with_time(
                "Couldn't check for existence of %s. Here's why: %s: %s",
                TABLE_NAME,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
    return exists


def _create_table(dynamodb_client: 'botocore.client.DynamoDB',
                 dynamodb_resource: 'boto3.resources.factory.dynamodb.ServiceResource',
                 table_name: str):
    try:
        table = dynamodb_resource.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'N'
                },
            ],
            BillingMode='PROVISIONED',
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
        table.wait_until_exists()
        utils.print_with_time('Table created successfully!')
    except dynamodb_client.exceptions.ResourceInUseException:
        utils.print_with_time(f'ResourceInUseException. Probably, db {table_name} already exists.')
        table = dynamodb_resource.Table(table_name)
    return table


TABLE = _init_table()
