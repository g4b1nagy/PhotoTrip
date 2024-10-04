import json
import subprocess

from utils.datetime import parse_datetime


TIMEOUT = 5


class ExifException(Exception):
    pass


def get_metadata(file_path=None, file_contents=None, timeout=TIMEOUT):
    if file_path is None and file_contents is None:
        raise ExifException("Either file_path or file_contents must be provided.")
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
    return metadata["File"]["FileTypeExtension"]["val"].strip()


def get_mime_type(metadata):
    return metadata["File"]["MIMEType"]["val"].strip()


def get_image_width_image_height(metadata):
    try:
        image_size = metadata["Composite"]["ImageSize"]["num"]
        # ImageSize may contain float values e.g. in svg files.
        if "." not in image_size:
            return [int(x) for x in image_size.split(" ")]
    except KeyError:
        return None, None


def get_megapixels(metadata):
    try:
        return float(metadata["Composite"]["Megapixels"]["num"])
    except KeyError:
        return None


def get_taken_on(metadata):
    values = []
    try:
        # SubSecDateTimeOriginal should offer the best precision. It may or may not
        # contain time zone information.
        values.append(metadata["Composite"]["SubSecDateTimeOriginal"]["val"])
    except KeyError:
        pass
    try:
        # DateTimeOriginal does not contain time zone information.
        values.append(metadata["EXIF"]["DateTimeOriginal"]["val"])
    except KeyError:
        pass
    for value in values:
        taken_on = parse_datetime(value)
        if taken_on is not None:
            return taken_on.isoformat()
    return None


def get_gps_latitude_gps_longitude(metadata):
    try:
        gps_position = metadata["Composite"]["GPSPosition"]["num"]
        return [float(x) for x in gps_position.split(" ")]
    except KeyError:
        return None, None


def get_gps_altitude(metadata):
    try:
        return float(metadata["Composite"]["GPSAltitude"]["num"])
    except KeyError:
        return None


def get_camera_make_model_serial_number(metadata):
    try:
        make = str(metadata["EXIF"]["Make"]["val"]).strip()
    except KeyError:
        make = ""
    try:
        model = str(metadata["EXIF"]["Model"]["val"]).strip()
    except KeyError:
        model = ""
    try:
        serial_number = str(metadata["EXIF"]["SerialNumber"]["val"]).strip()
    except KeyError:
        serial_number = ""
    return make, model, serial_number


def get_lens_make_name_serial_number(metadata):
    try:
        make = str(metadata["EXIF"]["LensMake"]["val"]).strip()
    except KeyError:
        make = ""
    try:
        name = str(metadata["Composite"]["LensID"]["val"]).strip()
    except KeyError:
        name = ""
    try:
        serial_number = str(metadata["EXIF"]["LensSerialNumber"]["val"]).strip()
    except KeyError:
        serial_number = ""
    return make, name, serial_number
