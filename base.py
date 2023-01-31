import config as cfg
import utils

import boto3
import botocore
from botocore.exceptions import ClientError
from typing import Any

TABLE_NAME = 'weather-bot-chats'
TABLE = None


def get_chats_with_params() -> dict[int, dict[str, Any]]:
    # return {534111842, 253766343, -1001899507998, -1001889227859, 899881657}
    #         me       , Leh      ,test_group_bots,      monastery, l}
    if not cfg.IN_AWS_LAMBDA:
        return {
            534111842:
                {'id': 534111842,
                'dark_mode': False,
                'cities' : [
                    'Вышний Волочек',
                    'мухосранск'
                    ]
                },
            -1001899507998:
                {'id': -1001899507998,
                'cities' : [
                    'New York',
                    'Вышний Волочек'
                    ]
                },
        }
    response = TABLE.scan()
    items = response['Items']
    items = {item['id']: item for item in items}
    return items


def get_chat_with_params(chat_id: int) -> dict:
    chats_with_params = get_chats_with_params()
    # chats_with_params = [c for c in chats_with_params if c['id'] == chat_id]
    return chats_with_params[chat_id]


def add_chat(chat_id: int) -> None:
    item = _get_item(chat_id)
    
    if not item:
        item = {'id': chat_id, 'cities': cfg.DEFAULT_CITY}
        TABLE.put_item(Item=item)
    
    utils.print_with_time(f'Chat {chat_id} added into the table')

    
def add_cities(chat_id: int, city_names: list[str]) -> list[str]:
    item = _get_item(chat_id)

    if not item:
        item = {'id': chat_id, 'cities': city_names}
        TABLE.put_item(Item=item)
        utils.print_with_time(f'Cities {city_names} added to {chat_id} in the table')
        return []
    else:
        old_cities = item.get('cities', [])
        new_cities = [city for city in city_names if city not in old_cities]
        all_cities = old_cities + new_cities
        item['cities'] = all_cities

        TABLE.put_item(Item=item)
        utils.print_with_time(f'Cities {new_cities} added to {chat_id} in the table')
        old_without_new_cities = [city for city in old_cities if city not in city_names]
        return old_without_new_cities

    
def clear_cities(chat_id: int) -> None:
    item = _get_item(chat_id)
    if not item:
        return
    item['cities'] = []
    TABLE.put_item(Item=item)
    utils.print_with_time(f'All cities cleared for {chat_id} in the table')


def list_cities(chat_id: int) -> list[str]:
    item = _get_item(chat_id)
    cities = item.get('cities', [])
    utils.print_with_time(f'List of cities for {chat_id}: {", ".join(cities)}')
    return cities


def switch_darkmode(chat_id: int) -> bool:
    item = _get_item(chat_id)
    dark_mode = item.get('dark_mode', cfg.DEFAULT_DARKMODE)
    dark_mode = not dark_mode
    
    item['dark_mode'] = dark_mode
    TABLE.put_item(Item=item)
    utils.print_with_time(f'Item {chat_id} with {dark_mode = }' \
                            f' has been put into the table')
    return dark_mode


def _get_item(chat_id: int) -> dict:
    try:
        response = TABLE.get_item(Key={'id': chat_id})
    except ClientError as err:
        utils.print_with_time(
            "Couldn't get chat %s from table %s. Here's why: %s: %s",
            chat_id, TABLE.name,
            err.response['Error']['Code'], err.response['Error']['Message'])
        raise
    else:
        return response.get('Item', {})


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
