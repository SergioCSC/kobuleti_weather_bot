from enum import Enum, auto
from typing import NamedTuple, Optional

class EventType(Enum):
    START = auto()
    HERE = auto()
    ADD_CRON_TRIGGER = auto()
    LIST_CRON_TRIGGERS = auto()
    CLEAR_CRON_TRIGGERS = auto()
    USER_LOCATION = auto()
    SCHEDULED = auto()
    CITY = auto()
    HOME_CITY = auto()
    ADD_CITY = auto()
    CHOOSE_CITY = auto()
    CLEAR_CITIES = auto()
    SHOW_CITIES = auto()
    LIST_CITIES = auto()
    SWITCH_DARKMODE = auto()
    OTHER = auto()


class EventData(NamedTuple):
    from_: str
    type: EventType
    chat_id: Optional[int]
    info: str
    # city_num: Optional[int]