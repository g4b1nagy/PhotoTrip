import json
import subprocess

from utils.datetime import parse_datetime


TIMEOUT = 5

# The values of the composite tags are derived from the values of other tags.
# These are convenience tags which are calculated after all other information is extracted.
# See:
# https://exiftool.org/TagNames/Composite.html
# https://exiv2.org/tags.html

#            Tag           |       Derived from
# -------------------------+--------------------------
#  SubSecDateTimeOriginal  | EXIF:DateTimeOriginal
#                          | SubSecTimeOriginal
#                          | OffsetTimeOriginal
# -------------------------+--------------------------
#  DateTimeOriginal        | DateTimeCreated
#                          | DateCreated
#                          | TimeCreated
# -------------------------+--------------------------
#  DateTimeOriginal        | ID3:RecordingTime
#                          | ID3:Year
#                          | ID3:Date
#                          | ID3:Time
# -------------------------+--------------------------
#  GPSDateTime             | GPS:GPSDateStamp
#                          | GPS:GPSTimeStamp
# -------------------------+--------------------------
#  GPSDateTime             | Parrot:GPSLatitude
#                          | Main:CreateDate
#                          | SampleTime
# -------------------------+--------------------------
#  GPSDateTime             | Sony:GPSDateStamp
#                          | Sony:GPSTimeStamp
# -------------------------+--------------------------
#  SubSecCreateDate        | EXIF:CreateDate
#                          | SubSecTimeDigitized
#                          | OffsetTimeDigitized
# -------------------------+--------------------------
#  DateTimeCreated         | IPTC:DateCreated
#                          | IPTC:TimeCreated
# -------------------------+--------------------------
#  DigitalCreationDateTime | IPTC:DigitalCreationDate
#                          | IPTC:DigitalCreationTime
# -------------------------+--------------------------
#  DateCreated             | Kodak:YearCreated
#                          | Kodak:MonthDayCreated
# -------------------------+--------------------------
#  SubSecModifyDate        | EXIF:ModifyDate
#                          | SubSecTime
#                          | OffsetTime

# EXIF:DateTimeOriginal (date/time when original image was taken)
# The date and time when the original image data was generated.
# For a digital still camera the date and time the picture was taken are recorded.

# EXIF:CreateDate (called DateTimeDigitized by the EXIF spec.)
# The date and time when the image was stored as digital data.

# EXIF:ModifyDate (called DateTime by the EXIF spec.)
# The date and time of image creation. In Exif standard, it is the date and time the file was changed.

TAKEN_ON_TAGS = [
    "SubSecDateTimeOriginal",
    "DateTimeOriginal",
    "GPSDateTime",
    "SubSecCreateDate",
    "DateTimeCreated",
    "DigitalCreationDateTime",
    "DateCreated",
    "SubSecModifyDate",
]

DURATION_TAGS = [
    # Number of occurrences in test data:
    # 6803 out of 8027 => 84.75146 %
    "QuickTime",
    # 175 out of 8027 => 2.18014 %
    "Composite",
    # 56 out of 8027 => 0.69764 %
    "M2TS",
    # 25 out of 8027 => 0.31144 %
    "MakerNotes",
    # 12 out of 8027 => 0.14949 %
    "Matroska",
    # 8 out of 8027 => 0.09966 %
    "ASF",
]


class ExifException(Exception):
    pass


def get_metadata(file_path=None, file_contents=None, timeout=TIMEOUT):
    if file_path is None and file_contents is None:
        raise ExifException("Either file_path or file_contents must be provided")
    if file_path is None:
        file_path = "-"
    try:
        process = subprocess.run(
            [
                # https://exiftool.org/exiftool_pod.html
                "exiftool",
                # Organize output by tag group
                "-groupHeadings",
                # Export/import tags in JSON format
                "-json",
                # Use long 2-line output format
                "-long",
                # Sort output alphabetically
                "-sort",
                file_path,
            ],
            # The input argument is passed to Popen.communicate() and thus to the
            # subprocess's stdin.
            input=file_contents,
            # If capture_output is true, stdout and stderr will be captured.
            capture_output=True,
            # A timeout may be specified in seconds, it is internally passed on to
            # Popen.communicate(). If the timeout expires, the child process will be
            # killed and waited for. The TimeoutExpired exception will be re-raised
            # after the child process has terminated.
            timeout=timeout,
        )
        stderr = process.stderr.decode(errors="replace")
        if stderr != "":
            raise ExifException(stderr)
        stdout = process.stdout.decode(errors="replace")
        metadata = json.loads(stdout)
        metadata = metadata[0]
        if process.returncode != 0:
            raise ExifException(metadata["ExifTool"]["Error"]["val"])
        return metadata
    except subprocess.TimeoutExpired as e:
        raise ExifException from e


def get_file_type(metadata):
    return metadata["File"]["FileTypeExtension"]["val"]


def get_mime_type(metadata):
    return metadata["File"]["MIMEType"]["val"]


def get_image_width_image_height(metadata):
    try:
        # ImageSize is more reliable than ImageWidth and ImageHeight
        # ImageSize may contain float values e.g. in some .svg files
        image_size = metadata["Composite"]["ImageSize"]["val"]
        image_size = [int(float(x)) for x in image_size.split("x")]
        return tuple(image_size)
    except KeyError:
        return None, None


def get_megapixels(metadata):
    try:
        return metadata["Composite"]["Megapixels"]["num"]
    except KeyError:
        return None


def get_taken_on(metadata):
    for tag in TAKEN_ON_TAGS:
        try:
            value = metadata["Composite"][tag]["val"]
            taken_on = parse_datetime(value)
            if taken_on is not None:
                return taken_on
        except KeyError:
            pass
    return None


def get_duration(metadata):
    # In test data, Duration could only be extracted for 7054 out of 8027 videos => 87.87841 %
    # Duration may contain strings e.g:
    # "QuickTime": {
    #     "Duration": {
    #         "desc": "Duration",
    #         "num": "0.00166666666666667",
    #         "val": "0.00 s"
    #     },
    for tag in DURATION_TAGS:
        try:
            return float(metadata[tag]["Duration"]["num"])
        except KeyError:
            pass
    return None


def get_gps_latitude_gps_longitude(metadata):
    try:
        gps_latitude = metadata["Composite"]["GPSLatitude"]["num"]
        gps_longitude = metadata["Composite"]["GPSLongitude"]["num"]
        return gps_latitude, gps_longitude
    except KeyError:
        return None, None


def get_gps_altitude(metadata):
    try:
        # Value will be:
        #  < 0 for "Below Sea Level" and
        # >= 0 for "Above Sea Level"
        return metadata["Composite"]["GPSAltitude"]["num"]
    except KeyError:
        return None


def get_camera_make_camera_model(metadata):
    try:
        camera_make = metadata["EXIF"]["Make"]["val"]
    except KeyError:
        camera_make = None
    try:
        camera_model = metadata["EXIF"]["Model"]["val"]
    except KeyError:
        camera_model = None
    return camera_make, camera_model


def get_lens_make_lens_model(metadata):
    # LensMake, LensModel may contain numeric values e.g:
    # "LensMake": {
    #     "desc": "Lens Make",
    #     "val": 0
    # },
    # "LensModel": {
    #     "desc": "Lens Model",
    #     "val": 1
    # },
    try:
        lens_make = str(metadata["EXIF"]["LensMake"]["val"])
    except KeyError:
        lens_make = None
    try:
        lens_model = str(metadata["EXIF"]["LensModel"]["val"])
    except KeyError:
        lens_model = None
    return lens_make, lens_model
