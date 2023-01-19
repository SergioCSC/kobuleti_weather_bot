# import boto3
# from botocore.exceptions import ResourceNotFoundException

# TABLE_NAME = 'weather-bot-chats'
# dynamodb = boto3.resource('dynamodb')


# def create_table(table_name: str) -> None:
#     try:
#         table = dynamodb.create_table(
#             TableName=table_name,
#             KeySchema=[
#                 {
#                     'Attribute_name': 'id',
#                     'key_type': 'HASH'
#                 },
#             ],
#             AttributeDefinitions=[
#                 {
#                     'attribute_name': 'id',
#                     'attribute_type': 'N'
#                 },
#             ]
#             # ProvisionedThroughput={
#             #     'ReadCapacityUnits': 5,
#             #     'WriteCapacityUnits': 5
#             # }
#         )
#         print("Table created successfully!")
#     except ResourceNotFoundException:
#         print("Resource not found.")


# create_table(TABLE_NAME)
# table = dynamodb.Table(TABLE_NAME)


def get_chat_set() -> set[int]:
    return {534111842, 253766343, -1001899507998, -1001889227859}
    # return {-1001899507998}
    create_table(TABLE_NAME)
    response = table.scan()
    items = response['Items']
    return set(item['id'] for item in items)


def add_chat(chat_id: int) -> None:
    return
    create_table(TABLE_NAME)
    item = {
        'id': chat_id,
    }
    table.put_item(Item=item)

    