import datetime

from utils.logging import get_logger


logger = get_logger(__name__)


DATETIME_FORMATS = [
    "%Y:%m:%d %H:%M:%S.%f%z",
    "%Y:%m:%d %H:%M:%S.%f",
    "%Y:%m:%d %H:%M:%S%z",
    "%Y:%m:%d %H:%M:%S",
]


def parse_datetime(dt_string):
    for format in DATETIME_FORMATS:
        try:
            dt = datetime.datetime.strptime(dt_string, format)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.UTC)
            return dt
        except ValueError:
            pass
    logger.error(f"Could not parse datetime string: {dt_string}")
    return None


def timestamp_to_datetime(timestamp):
    try:
        return datetime.datetime.fromtimestamp(timestamp).replace(tzinfo=datetime.UTC)
    except ValueError:
        logger.error(f"Could not convert timestamp to datetime: {timestamp}")
        return None
