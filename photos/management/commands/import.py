import pathlib
import os

from django.core.management.base import BaseCommand

from photos.models import Photo, FileType, MimeType, Camera, Lens
from utils import exif
from utils.logging import get_logger
from utils.datetime import timestamp_to_datetime


logger = get_logger(__name__)


class ImporterException(Exception):
    pass


class Command(BaseCommand):
    help = "Import photos from path"

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            type=str,
            help="Path to directory containing photos",
        )

    def handle(self, *args, **options):
        path = pathlib.Path(options["path"])
        if not path.exists():
            raise ImporterException(f"Path does not exist: {path}")
        if path.is_dir():
            file_paths = path.glob("**/*")
        elif path.is_file():
            file_paths = [path]
        else:
            raise ImporterException(f"Path is neither a directory nor a file: {path}")
        file_paths = sorted([x for x in file_paths if x.is_file()])
        if len(file_paths) == 0:
            raise ImporterException(f"No files found at: {path}")

        for file_path in file_paths:
            logger.info(f"Processing: {file_path}")
            try:
                metadata = exif.get_metadata(file_path=file_path)
            except exif.ExifException:
                logger.exception(f"Could not retrieve file metadata: {file_path}")
                continue
            file_type = exif.get_file_type(metadata)
            file_type, created = FileType.objects.update_or_create(
                name=file_type,
            )
            mime_type = exif.get_mime_type(metadata)
            mime_type, created = MimeType.objects.update_or_create(
                name=mime_type,
            )
            image_width, image_height = exif.get_image_width_image_height(metadata)
            megapixels = exif.get_megapixels(metadata)
            taken_on = exif.get_taken_on(metadata)
            gps_latitude, gps_longitude = exif.get_gps_latitude_gps_longitude(metadata)
            gps_altitude = exif.get_gps_altitude(metadata)
            camera_make, camera_model = exif.get_camera_make_camera_model(metadata)
            if camera_make is not None or camera_model is not None:
                camera, created = Camera.objects.update_or_create(
                    make=camera_make or "",
                    model=camera_model or "",
                )
            else:
                camera = None
            lens_make, lens_model = exif.get_lens_make_lens_model(metadata)
            if lens_make is not None or lens_model is not None:
                lens, created = Lens.objects.update_or_create(
                    make=lens_make or "",
                    model=lens_model or "",
                )
            else:
                lens = None
            stat = os.stat(file_path)
            photo, created = Photo.objects.update_or_create(
                file_name=file_path.name,
                file_path=file_path,
                file_size=stat.st_size,
                file_atime=timestamp_to_datetime(stat.st_atime),
                file_mtime=timestamp_to_datetime(stat.st_mtime),
                file_ctime=timestamp_to_datetime(stat.st_ctime),
                file_type=file_type,
                mime_type=mime_type,
                image_width=image_width,
                image_height=image_height,
                megapixels=megapixels,
                taken_on=taken_on,
                gps_latitude=gps_latitude,
                gps_longitude=gps_longitude,
                gps_altitude=gps_altitude,
                camera=camera,
                lens=lens,
                metadata=metadata,
            )
            photo.save()
