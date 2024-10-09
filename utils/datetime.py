import datetime

from utils.logging import get_logger


logger = get_logger(__name__)


DATETIME_FORMATS = [
    "%Y:%m:%d %H:%M:%S.%f%z",
    "%Y:%m:%d %H:%M:%S.%f",
    "%Y:%m:%d %H:%M:%S%z",
    "%Y:%m:%d %H:%M:%S",
]


def parse_datetime(string):
    for format in DATETIME_FORMATS:
        try:
            dt = datetime.datetime.strptime(string, format)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=datetime.UTC)
            else:
                return dt
        except ValueError:
            pass
    logger.error(f"Could not parse datetime string: {string}")
    return None


def timestamp_to_datetime(timestamp):
    try:
        return datetime.datetime.fromtimestamp(timestamp, tz=datetime.UTC)
    except (ValueError, OSError, OverflowError):
        logger.error(f"Could not convert timestamp to datetime: {timestamp}")
        return None
