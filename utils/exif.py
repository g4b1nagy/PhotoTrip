import json
import subprocess

from utils.datetime import parse_datetime


TIMEOUT = 5
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
        # Note that image_size may contain float values e.g. in some .svg files
        image_size = metadata["Composite"]["ImageSize"]["val"]
        image_size = [int(x) for x in image_size.split("x")]
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
    try:
        lens_make = metadata["EXIF"]["LensMake"]["val"]
    except KeyError:
        lens_make = None
    try:
        lens_model = metadata["EXIF"]["LensModel"]["val"]
    except KeyError:
        lens_model = None
    return lens_make, lens_model
