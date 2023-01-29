import config as cfg
import utils

import boto3
import botocore
from botocore.exceptions import ClientError

TABLE_NAME = 'weather-bot-chats'
TABLE = None


def get_chats_with_params() -> list[dict]:
    # return {534111842, 253766343, -1001899507998, -1001889227859, 899881657}
    #         me       , Leh      ,test_group_bots,      monastery, l}
    if not cfg.IN_AWS_LAMBDA:
        return {
            534111842: 
                {'dark_mode': False,
                 'cities' : [
                        'Вышний Волочек',
                        'мухосранск'
                    ]
                 },
            -1001899507998:
                {'cities' : [
                        'New York',
                        'f',
                        'Вышний Волочек'
                    ]
                 },
        }
    response = TABLE.scan()
    items = response['Items']
    return items


def add_chat(chat_id: int) -> None:
    item = _get_item(chat_id)
    
    if not item:
        item = {'id': chat_id}
        TABLE.put_item(Item=item)
    
    utils.print_with_time(f'Item {chat_id} has been put into the table')


def switch_darkmode(chat_id: int) -> bool:
    item = _get_item(chat_id)
    dark_mode = item.get('dark_mode', cfg.DEFAULT_DARKMODE)
    dark_mode = not dark_mode
    item = {'id': chat_id, 'dark_mode': dark_mode}
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
