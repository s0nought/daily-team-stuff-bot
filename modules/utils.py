import json
from datetime import datetime, date, timezone

from .constants import (
    FIRST_PLANNING_DATETIME_UTC
)

def load_json(file_path: str, mode: str = "rt", encoding: str = "UTF-8"):
    with open(file_path, mode = mode, encoding = encoding) as f:
        return json.load(f)

def dump_json(data, file_path: str, mode: str = "wt", encoding: str = "UTF-8", indent: int = 4) -> None:
    with open(file_path, mode = mode, encoding = encoding) as f:
        return json.dump(data, f, indent = indent)

def get_datetime() -> datetime:
    return datetime.now(timezone.utc)

def format_datetime(dt: datetime, f: str = r"%d.%m.%Y %H:%M") -> str:
    return dt.strftime(f)

def get_current_date() -> str:
    return format_datetime(get_datetime(), r"%d.%m")

def get_weekday() -> int:
    return date.isoweekday(get_datetime())

def is_friday() -> bool:
    return True if get_weekday() == 5 else False

def is_weekend() -> bool:
    return True if get_weekday() > 5 else False

def is_planning_day() -> bool:
    x = (get_datetime() - FIRST_PLANNING_DATETIME_UTC).days
    return True if x % 14 == 0 else False
