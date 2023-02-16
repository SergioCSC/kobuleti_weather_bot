from typing import NamedTuple, Optional
from functools import cache


class TimeOfDay(NamedTuple):
    hours: int
    minutes: Optional[int]
    

@cache
def parse_time(time_str: str) -> Optional[TimeOfDay]:
    multiplier = -1 if time_str[0] == '-' else 1
    if time_str[0] in '+-':
        time_str = time_str[1:]

    for possible_delimeter in (':', '_', '.', ',', 'ю', 'б'):
        time_str = time_str.replace(possible_delimeter, ':')
        
    tokens = [token.strip() for token in time_str.split(':')]
    if not tokens or not all(token.isdigit() for token in tokens):
        return None
    tokens = [int(st) for st in tokens]
    tokens = tokens[:2]
    hours = tokens[0]
    
    if not 0 <= hours < 24:
        return None
    
    minutes = 0
    if len(tokens) == 2:
        minutes = tokens[1]
        if not 0 <= minutes < 60:
            return None
    
    return TimeOfDay(hours * multiplier, minutes * multiplier)
