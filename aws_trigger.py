from utils import print_with_time
from time_of_day import TimeOfDay, parse_time

import boto3
import botocore

import json
import logging
from typing import Optional
from typing import NamedTuple
from enum import Enum, auto
from functools import cache
import time


RETRY_ATTEMPTS = 0
MAXIMUM_AGE_OF_EVENT_IN_SECONDS = 60


class TimeZone(NamedTuple):
    hours: int
    minutes: int


class Weekday(Enum):
    SUNDAY = auto()
    MONDAY = auto()
    TUESDAY = auto()
    WEDNESDAY = auto()
    THURSDAY = auto()
    FRIDAY = auto()
    SATURDAY = auto()


@cache
def time_2_str(time: TimeOfDay, weekday: Weekday) -> str:
    if weekday:
        weekday = ['воскресенье', 
                'понедельник', 
                'вторник', 
                'среда', 
                'четверг', 
                'пятница', 
                'суббота'][weekday.value - 1]
    return f"{weekday + ', ' if weekday else ''}{time.hours:02}:{time.minutes:02}"


@cache
def _parse_time_str(time_str: str) -> tuple[Optional[TimeOfDay], Optional[Weekday]]:

    tokens = time_str.strip().lower().split()
    
    if not tokens or len(tokens) > 2:
        return None, None
    
    if len(tokens) == 1:
        return parse_time(tokens[0]), None
    
    if len(tokens) == 2:
        if time_of_day := parse_time(tokens[0]):
            weekday_str = tokens[1]
        else:
            time_of_day = parse_time(tokens[1])
            weekday_str = tokens[0]
        
        weekday = [d for d in Weekday if d.name.lower() == weekday_str]
        if weekday:
            return time_of_day, weekday[0]
        
        weekday_names_rus = [('воскресенье', 'вс'), 
                             ('понедельник', 'пн'),
                             ('вторник', 'вт'), 
                             ('среда', 'ср'),
                             ('четверг', 'чт'),
                             ('пятница', 'пт'),
                             ('суббота', 'сб'),
                             ]    
        weekday = [d for i, d in enumerate(Weekday) 
                if weekday_str in weekday_names_rus[i]]
        if weekday:
            return time_of_day, weekday[0]
        
        return None, None


@cache
def _add_time_shift(time_of_day: TimeOfDay, weekday: Optional[Weekday], 
        time_shift: TimeOfDay) -> tuple[TimeOfDay, Weekday, bool]:

    minutes = time_of_day.minutes + time_shift.minutes
    hours = time_of_day.hours + time_shift.hours
    
    if minutes >= 60:
        minutes -= 60
        hours += 1
    
    if minutes < 0:
        minutes += 60
        hours -= 1
        
    additional_day = 0
    
    if hours >= 24:
        hours -= 24
        additional_day = 1
    
    if hours < 0:
        hours += 24
        additional_day = -1

    if weekday and additional_day:
        day_value = (weekday.value + additional_day) % len(Weekday)
        if day_value == 0:
            day_value += len(Weekday)
        weekday = Weekday(day_value)

    return TimeOfDay(hours, minutes), weekday


def _create_cron_expression(time_of_day: TimeOfDay, weekday: Weekday) -> str:
    hours = time_of_day.hours
    minutes = time_of_day.minutes
    
    return f'cron({minutes} {hours} ? * {weekday.value if weekday else "*"} *)'
    

def get_aws_rules(chat_id: int, context) -> list[str]:
    print_with_time(f'Start: get_aws_triggers\n\n')
    client = boto3.client(service_name='events', region_name='us-east-1')
    
    response = client.list_rule_names_by_target(
        TargetArn = context.invoked_function_arn
    )

    rule_names = response.get('RuleNames')
    rule_names = [r for r in rule_names if r not in ('run_every_day', 'MyCronRule_9000')]
    rule_names = [r for r in rule_names if r.endswith(str(chat_id))]
    # print_with_time(f'client.list_rule_names_by_target response: {response}\n\n')
    return rule_names


def clear_aws_rules(chat_id: int, context) -> None:
    print_with_time(f'Start: clear_aws_triggers\n\n')
    client_events = boto3.client(service_name='events', region_name='us-east-1')
    client_lambda = boto3.client(service_name='lambda', region_name='us-east-1')
    
    # remove permissions
    response = client_lambda.get_policy(
        FunctionName=context.function_name,
    )
    for statement in json.loads(response.get('Policy', '{}')).get('Statement', {}):
        statement_id = statement.get('Sid', '')
        print_with_time(f'{statement_id = }')
        if statement_id.endswith(str(chat_id)):
            try:
                response = client_lambda.remove_permission(
                    FunctionName=context.function_name,
                    StatementId=statement_id,
                )
            except botocore.exceptions.ClientError as e:
                if err := e.response['Error']['Code'] \
                        in ('ResourceConflictException', 
                            'ResourceNotFoundException'):
                    print_with_time(f'{err = }, {e = }', logging.INFO)
                else:
                    raise e
    
    #remove rules
    rule_names = get_aws_rules(chat_id, context)
    for rule_name in rule_names:
        try:
            response = client_events.remove_targets(Rule=rule_name, 
                                            Ids=[context.function_name])
            if isinstance(response, dict) \
                    and response.get('FailedEntryCount', 0):
                failed_entries = response.get('FailedEntries', [])
                print_with_time(f'{failed_entries = }', logging.INFO)
            response = client_events.delete_rule(Name=rule_name)
            response = client_lambda.remove_permission(
                FunctionName=context.function_name,
                StatementId=rule_name,
            )
            # time.sleep(1)
        except botocore.exceptions.ClientError as e:
            err = e.response['Error']['Code']
            print_with_time(f'{rule_name = }   {err = }   {e = }', logging.INFO)
            if not err in ('ResourceConflictException', 
                           'ResourceNotFoundException'):
                raise e


def _list_all_targets(chat_id: int, context):
    rule_names = get_aws_rules(chat_id, context)
    client_events = boto3.client(service_name='events', region_name='us-east-1')
    
    rules_targets = []
    for rule in rule_names:
        rule_targets = client_events.list_targets_by_rule(Rule=rule).get('Targets', [])
        rules_targets.extend(rule_targets)
    target_ids = [target['Id'] for target in rules_targets if 'Id' in target]
    return target_ids


def _cut_timestamp(rule_name: str) -> str:
    return '_'.join(rule_name.split('_')[2:])
    

def make_aws_rule(chat_id: int, time_str: str, timezone: TimeOfDay, context) \
        -> tuple[Optional[TimeOfDay], Optional[Weekday]]:
            
    print_with_time(f'Start: make_aws_trigger\n\n')
    
    time_of_day, weekday = _parse_time_str(time_str)
    if not time_of_day:
        return None, None

    time_shift = TimeOfDay(-timezone.hours, -timezone.minutes)
    shifted_time_of_day, shifted_weekday = _add_time_shift(time_of_day, weekday, time_shift)

    cron_expression = _create_cron_expression(shifted_time_of_day, shifted_weekday)
    # cron_expression = 'cron(1 13 ? * 7 *)'
    client = boto3.client(service_name='events', region_name='us-east-1')
    
    h = shifted_time_of_day.hours
    m = shifted_time_of_day.minutes
    w = shifted_weekday.name + '_' if shifted_weekday else ''
    timestamp = int(time.time())
    rule_name = f'ts_{timestamp}_{w}{h:02}_{m:02}_chat_{chat_id}'
    
    existing_rules = get_aws_rules(chat_id, context)
    existing_rules = [_cut_timestamp(e) for e in existing_rules]
    cutted_rule_name = _cut_timestamp(rule_name)
    
    if cutted_rule_name in existing_rules:
        return time_of_day, weekday
    
    response = client.put_rule(
        Name = rule_name,
        ScheduleExpression = cron_expression,  # 'cron(0/5 * * * ? 2111)',
        State = 'ENABLED',
    )
    
    print_with_time(f'client.put_rule response: {response}\n\n')
    rule_arn = response['RuleArn']

    response = client.put_targets(
        Rule = rule_name,
        Targets=[
            {
                'Id': context.function_name,
                'Arn': context.invoked_function_arn,
                'RetryPolicy': {
                    'MaximumRetryAttempts': RETRY_ATTEMPTS,
                    'MaximumEventAgeInSeconds': MAXIMUM_AGE_OF_EVENT_IN_SECONDS,
                },
            },
        ]
    )
    
    print_with_time(f'client.put_targets response: {response}\n\n')
    
    lambda_client = boto3.client(service_name='lambda', region_name='us-east-1')
    try:
        response = lambda_client.add_permission(
            FunctionName=context.invoked_function_arn,
            StatementId=rule_name,
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=rule_arn
        )
    except botocore.exceptions.ClientError as error:
        exception_name = error.response['Error']['Code']
        if exception_name == 'ResourceConflictException':
            print_with_time(f'{exception_name}: {error}', logging.ERROR)
        else:
            raise error

    print_with_time(f'client.add_permission response: {response}\n\n')

    return time_of_day, weekday