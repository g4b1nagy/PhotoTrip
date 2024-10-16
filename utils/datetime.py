import datetime
import os
import re

from utils.logging import get_logger


logger = get_logger(__name__)


PARSE_DATETIME_FORMATS = [
    "%Y:%m:%d %H:%M:%S.%f%z",
    "%Y:%m:%d %H:%M:%S.%f",
    "%Y:%m:%d %H:%M:%S%z",
    "%Y:%m:%d %H:%M:%S",
]

# Equivalent to +15:59:59
# See: https://www.postgresql.org/message-id/10520.1338415812%40sss.pgh.pa.us
MAX_TIME_ZONE_DISPLACEMENT_SECONDS = 57599

# Time zone to default to when time zone information is missing or invalid
TIME_ZONE = datetime.UTC

MONTH_NAMES = {
    # Month names
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    # Month name abbreviations
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
    # Alternative month name abbreviations
    "ian": 1,
    "mai": 5,
    "iun": 6,
    "iul": 7,
    "noi": 11,
}
MONTH_NAME = "|".join(MONTH_NAMES.keys())
MONTH_NAME = rf"""(?P<month_name>{MONTH_NAME})"""

# \s == Unicode whitespace character
# \d == Unicode decimal digit
# \D == Unicode non-decimal digit

# whitespace or - or . or : or _
SEPARATOR = r"""(?:\s|-|\.|:|_)"""

PATH_SEPARATOR = re.escape(os.sep)

# 1000 => 2999
YEAR = r"""(?P<year>[12][0-9][0-9][0-9])"""

# 01 or 02 or 03 or ... or 10 or 11 or 12
MONTH = r"""(?P<month>0[1-9]|1[012])"""

# 01 or 02 or 03 or ... or 29 or 30 or 31
DAY = r"""(?P<day>0[1-9]|1[0-9]|2[0-9]|3[01])"""

# 00 or 01 or 02 or ... or 21 or 22 or 23
HOUR = r"""(?P<hour>[0-1][0-9]|2[0123])"""

# 00 or 01 or 02 or ... or 57 or 58 or 59
MINUTE = r"""(?P<minute>[0-5][0-9])"""

# 00 or 01 or 02 or ... or 57 or 58 or 59
SECOND = r"""(?P<second>[0-5][0-9])"""

# 000 => 999
MILLISECOND = r"""(?P<millisecond>[0-9][0-9][0-9])"""

# 000,000 => 999,999
MICROSECOND = r"""(?P<microsecond>[0-9][0-9][0-9][0-9][0-9][0-9])"""

EXTRACT_DATETIME_FORMATS = [
    rf"""\D(IMG|PXL|VID)_{YEAR}{MONTH}{DAY}_{HOUR}:{MINUTE}:{SECOND}\D""",
    rf"""\D(IMG|PXL|VID)_{YEAR}{MONTH}{DAY}_{HOUR}{MINUTE}{SECOND}\D""",
    rf"""\D(IMG|PXL|VID)_{YEAR}{MONTH}{DAY}_{HOUR}{MINUTE}{SECOND}{MILLISECOND}\D""",
    rf"""\D(IMG|VID)-{YEAR}{MONTH}{DAY}\D""",
    rf"""\D(IMG|VID)_{YEAR}{MONTH}{DAY}\D""",
    rf"""\D{DAY}{SEPARATOR}{MONTH_NAME}{SEPARATOR}{YEAR}\D""",
    rf"""\D{YEAR}-{MONTH}-{DAY} AT {HOUR}\.{MINUTE}\.{SECOND}\D""",
    rf"""\D{YEAR}-{MONTH}-{DAY} {HOUR}-{MINUTE}-{SECOND}\D""",
    rf"""\D{YEAR}-{MONTH}-{DAY} {HOUR}:{MINUTE}:{SECOND}\D""",
    rf"""\D{YEAR}-{MONTH}-{DAY}-{HOUR}_{MINUTE}_{SECOND}\D""",
    rf"""\D{YEAR}-{MONTH}-{DAY}-{HOUR}H{MINUTE}M{SECOND}S{MILLISECOND}\D""",
    rf"""\D{YEAR}-{MONTH}-{DAY}-{HOUR}{MINUTE}{SECOND}\D""",
    rf"""\D{YEAR}-{MONTH}-{DAY}\D""",
    rf"""\D{YEAR}-{MONTH}-{DAY}_{HOUR}-{MINUTE}-{SECOND}\D""",
    rf"""\D{YEAR}\.{MONTH}\.{DAY}\D""",
    rf"""\D{YEAR}_{MONTH}_{DAY}T{HOUR}_{MINUTE}_{SECOND}_{MILLISECOND}\D""",
    rf"""\D{YEAR}{MONTH}{DAY}-{HOUR}{MINUTE}{SECOND}\D""",
    rf"""\D{YEAR}{MONTH}{DAY}_{HOUR}{MINUTE}{SECOND}\D""",
    rf"""\D{YEAR}{MONTH}{DAY}_{HOUR}{MINUTE}{SECOND}_{MILLISECOND}\D""",
    rf"""{PATH_SEPARATOR}{YEAR}{PATH_SEPARATOR}""",
]
EXTRACT_DATETIME_FORMATS = [
    re.compile(x, re.IGNORECASE) for x in EXTRACT_DATETIME_FORMATS
]


def parse_datetime(string):
    for format in PARSE_DATETIME_FORMATS:
        try:
            dt = datetime.datetime.strptime(string, format)
            if dt.tzinfo is not None:
                if (
                    abs(dt.tzinfo.utcoffset(None).total_seconds())
                    > MAX_TIME_ZONE_DISPLACEMENT_SECONDS
                ):
                    logger.error(
                        f"Time zone displacement out of range: {dt}, using time zone: {TIME_ZONE} instead"
                    )
                    return dt.replace(tzinfo=TIME_ZONE)
                else:
                    return dt
            else:
                return dt.replace(tzinfo=TIME_ZONE)
        except ValueError:
            pass
    logger.error(f"Could not parse datetime string: {string}")
    return None


def extract_datetime(file_path):
    # Postel's law
    file_path = str(file_path)
    matches = []
    for format in EXTRACT_DATETIME_FORMATS:
        for match in re.finditer(format, file_path):
            matches.append(match)
    if len(matches) == 0:
        return None

    # Sort by (rightmost, longest) first
    matches.sort(key=lambda x: (x.start(), x.end() - x.start()), reverse=True)
    group_dict = matches[0].groupdict()
    if "month_name" in group_dict:
        group_dict["month"] = MONTH_NAMES[group_dict["month_name"].lower()]
    try:
        return datetime.datetime(
            year=int(group_dict.get("year")),
            month=int(group_dict.get("month", 1)),
            day=int(group_dict.get("day", 1)),
            hour=int(group_dict.get("hour", 0)),
            minute=int(group_dict.get("minute", 0)),
            second=int(group_dict.get("second", 0)),
            microsecond=int(group_dict.get("millisecond", 0)) * 1000,
            tzinfo=datetime.UTC,
        )
    except ValueError:
        logger.error(f"Could not construct datetime from group_dict: {group_dict}")
        return None


def timestamp_to_datetime(timestamp):
    try:
        return datetime.datetime.fromtimestamp(timestamp, tz=TIME_ZONE)
    except (ValueError, OSError, OverflowError):
        logger.error(f"Could not convert timestamp to datetime: {timestamp}")
        return None
