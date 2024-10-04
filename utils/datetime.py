import datetime

from utils.logging import get_logger


logger = get_logger(__name__)


def parse_datetime(string):
    formats = [
        "%Y:%m:%d %H:%M:%S.%f%z",
        "%Y:%m:%d %H:%M:%S.%f",
        "%Y:%m:%d %H:%M:%S%z",
        "%Y:%m:%d %H:%M:%S",
        "%Y:%m:%d",
    ]
    for format in formats:
        try:
            dt = datetime.datetime.strptime(string, format)
            if dt.tzinfo is None:
                dt = dt.astimezone()
            return dt
        except ValueError:
            pass
    logger.error(f"Could not parse datetime string: {string}")
    return None
