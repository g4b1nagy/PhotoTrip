import datetime

from utils.logging import get_logger


logger = get_logger(__name__)


DATETIME_FORMATS = [
    "%Y:%m:%d %H:%M:%S.%f%z",
    "%Y:%m:%d %H:%M:%S.%f",
    "%Y:%m:%d %H:%M:%S%z",
    "%Y:%m:%d %H:%M:%S",
]

# Equivalent to +15:59:59
# See: https://www.postgresql.org/message-id/10520.1338415812%40sss.pgh.pa.us
MAX_TIME_ZONE_DISPLACEMENT_SECONDS = 57599
TIMEZONE = datetime.UTC


def parse_datetime(string):
    for format in DATETIME_FORMATS:
        try:
            dt = datetime.datetime.strptime(string, format)
            if dt.tzinfo is not None:
                if abs(dt.tzinfo.utcoffset(None).total_seconds()) > MAX_TIME_ZONE_DISPLACEMENT_SECONDS:
                    logger.error(f"Time zone displacement out of range: {dt}")
                    logger.error(f"Using time zone: {TIMEZONE} instead")
                    return dt.replace(tzinfo=TIMEZONE)
                else:
                    return dt
            else:
                return dt.replace(tzinfo=TIMEZONE)
        except ValueError:
            pass
    logger.error(f"Could not parse datetime string: {string}")
    return None


def timestamp_to_datetime(timestamp):
    try:
        return datetime.datetime.fromtimestamp(timestamp, tz=TIMEZONE)
    except (ValueError, OSError, OverflowError):
        logger.error(f"Could not convert timestamp to datetime: {timestamp}")
        return None
