from enum import Enum, auto
from typing import NamedTuple, Optional

class EventType(Enum):
    SCHEDULED = auto()
    CITY = auto()
    ADD_CITY = auto()
    CHOOSE_CITY = auto()
    CLEAR_CITIES = auto()
    SHOW_CITIES = auto()
    LIST_CITIES = auto()
    SWITCH_DARKMODE = auto()
    OTHER = auto()


class EventData(NamedTuple):
    type: EventType
    chat_id: Optional[int]
    city_name: str
    city_num: Optional[int]