import config as cfg
from city import City
from event import EventData, EventType
import utils

import boto3
import botocore
from botocore.exceptions import ClientError

import time
from typing import Any
from decimal import Decimal

TABLE_NAME = 'weather-bot-chats'
CITY_KEYS = ('cities', 'last_command_city_options', 'chat_city')
TABLE = None


def get_chats() -> dict[int, dict[str, Any]]:
    response = TABLE.scan()
    chats = response['Items']
    chats = {chat['id']: chat for chat in chats}
    
    if not cfg.IN_AWS_LAMBDA:
        chats = {k: v for k, v in chats.items() if k in (534111842, -1001899507998)}
    
    for chat in chats.values():
        _chat_decimals_to_cities(chat)
    
    return chats


def _get_chat(chat_id: int) -> dict[str, Any]:
    chats_with_params = get_chats()
    return chats_with_params.get(chat_id, {'id': chat_id})


def _put_chat(chat: dict) -> None:
    _chat_cities_to_decimals(chat)
    TABLE.put_item(Item=chat)


def save_chat_city(chat_id: int, chat_city: City) -> None:
    chat = _get_chat(chat_id)
    chat['chat_city'] = [chat_city]
    chat['chat_city_last_update_timestamp'] = int(time.time())
    _put_chat(chat)
    
    utils.print_with_time(f'City {chat_city} saved as chat city')
    return


def clear_chat_city(chat_id: int) -> None:
    chat = _get_chat(chat_id)
    chat.pop('chat_city', None)
    chat.pop('chat_city_last_update_timestamp', None)
    _put_chat(chat)
    
    utils.print_with_time(f'chat city cleared for chat {chat_id}')
    return
    

def load_chat_city(chat_id: int) -> City:
    chat = _get_chat(chat_id)
    last_update_timestamp = chat.get('chat_city_last_update_timestamp')
    if not last_update_timestamp:
        return None
    time_delta = int(time.time()) - int(last_update_timestamp)
    if time_delta > cfg.CHAT_CITY_EXPIRATION_TIME_SEC:
        return None
    
    chat_cities = chat.get('chat_city')
    if not chat_cities:
        return None
    return chat_cities[0]


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


def add_city(chat_id: int, new_city: City) -> list[str]:
    chat = _get_chat(chat_id)

    old_cities = chat.get('cities', [])
    if new_city not in old_cities:
        chat['cities'] = old_cities + [new_city]
        _put_chat(chat)
        
    utils.print_with_time(f'City {new_city} added to {chat_id} in the table')
    old_without_new_cities = [c for c in old_cities if c != new_city]
    return old_without_new_cities

    
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


def _decimal_to_city(decimal_city: tuple) -> City:
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
    for key in CITY_KEYS:
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
    for key in CITY_KEYS:
        if key in chat:
            chat[key] = [_city_to_decimal(c) for c in chat[key] if isinstance(c, City)]
    


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
