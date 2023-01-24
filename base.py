import config as cfg

import boto3
import botocore
from botocore.exceptions import ClientError

TABLE_NAME = 'weather-bot-chats'
TABLE = None


def init_table() -> 'boto3.resources.factory.dynamodb.Table':
    dynamodb_client = boto3.client('dynamodb', region_name=cfg.AWS_REGION)
    dynamodb_resource = boto3.resource('dynamodb', region_name=cfg.AWS_REGION)
    table = create_table(dynamodb_client, dynamodb_resource, TABLE_NAME)

    print(f'{dynamodb_client = }, {type(dynamodb_client) = }')
    print(f'{dynamodb_resource = }, {type(dynamodb_resource) = }')
    print(f'{table = }, {type(table) = }')
    
    return table


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
        print('Table created successfully!')
    except dynamodb_client.exceptions.ResourceInUseException:
        print(f'ResourceInUseException. Probably, db {table_name} already exists.')
        table = dynamodb_resource.Table(table_name)
    return table


def get_chat_set() -> set[int]:
    # return {534111842, 253766343, -1001899507998, -1001889227859}
    #         me       , Leha     ,test_group_bots,      monastery}
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
    print(f'Item {chat_id} putted into the table')
    

TABLE = init_table()
