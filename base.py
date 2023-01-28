import config as cfg
import utils

import boto3
import botocore
from botocore.exceptions import ClientError

TABLE_NAME = 'weather-bot-chats'
TABLE = None


def init_table() -> 'boto3.resources.factory.dynamodb.Table':
    utils.print_with_time('START TABLE INITIALIZATION')
    dynamodb_client = boto3.client('dynamodb', region_name=cfg.AWS_REGION)
    dynamodb_resource = boto3.resource('dynamodb', region_name=cfg.AWS_REGION)
    
    table = dynamodb_resource.Table(TABLE_NAME)
    if check_if_table_exists(table):
        utils.print_with_time('FINISH TABLE INITIALIZATION')
        return table
    
    table = create_table(dynamodb_client, dynamodb_resource, TABLE_NAME)
    
    utils.print_with_time('FINISH TABLE INITIALIZATION')
    return table


def check_if_table_exists(table: 'boto3.resources.factory.dynamodb.Table') -> bool:
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


def create_table(dynamodb_client: 'botocore.client.DynamoDB',
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


def get_chat_set() -> set[int]:
    # return {534111842, 253766343, -1001899507998, -1001889227859, }
    #         me       , Leh      ,test_group_bots,      monastery, l}
    if not cfg.IN_AWS_LAMBDA:
        return {534111842, -1001899507998}
    response = TABLE.scan()
    items = response['Items']
    return set(item['id'] for item in items)


def add_chat(chat_id: int) -> None:
    TABLE.load()
    item = {
        'id': chat_id,
    }
    TABLE.put_item(Item=item)
    utils.print_with_time(f'Item {chat_id} has been put into the table')
    

TABLE = init_table()
