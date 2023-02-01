from typing import NamedTuple


class City(NamedTuple):
    local_name: str
    iso2: str
    country: str
    admin_subject: str
    lat: float
    lon: float
    asl: int
    population: int
    distance: float
    tz: str
    url_suffix_for_sig: str