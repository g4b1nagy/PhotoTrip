from utils.models import BaseModel
from django.db import models


class Photo(BaseModel):
    thumbnail = models.FileField()
    file_name = models.CharField(max_length=256)
    file_path = models.CharField(max_length=4096)

    # Fields derived from os.stat():
    file_size = models.PositiveBigIntegerField()
    file_atime = models.DateTimeField()
    file_mtime = models.DateTimeField()
    file_ctime = models.DateTimeField()

    # Fields derived from metadata:
    file_type = models.ForeignKey("FileType", on_delete=models.PROTECT)
    mime_type = models.ForeignKey("MimeType", on_delete=models.PROTECT)
    image_width = models.PositiveIntegerField(null=True)
    image_height = models.PositiveIntegerField(null=True)
    megapixels = models.FloatField(null=True)
    taken_on = models.DateTimeField(null=True)
    gps_latitude = models.FloatField(null=True)
    gps_longitude = models.FloatField(null=True)
    gps_altitude = models.FloatField(null=True)
    camera = models.ForeignKey("Camera", null=True, on_delete=models.SET_NULL)
    lens = models.ForeignKey("Lens", null=True, on_delete=models.SET_NULL)
    metadata = models.JSONField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["file_path"], name="unique_photo_file_path"
            ),
        ]

    def __str__(self):
        return self.file_name


class FileType(BaseModel):
    name = models.CharField(max_length=256)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_file_type"),
        ]

    def __str__(self):
        return self.name


class MimeType(BaseModel):
    name = models.CharField(max_length=256)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_mime_type"),
        ]

    def __str__(self):
        return self.name


class Camera(BaseModel):
    make = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    serial_number = models.CharField(max_length=64)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(make="")
                | ~models.Q(model="")
                | ~models.Q(serial_number=""),
                name="non_empty_camera",
            ),
            models.UniqueConstraint(
                fields=["make", "model", "serial_number"], name="unique_camera"
            ),
        ]

    def __str__(self):
        return f"{self.make} {self.model} {self.serial_number}"


class Lens(BaseModel):
    make = models.CharField(max_length=64)
    name = models.CharField(max_length=256)
    serial_number = models.CharField(max_length=64)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(name=""), name="non_empty_lens_name"
            ),
            models.UniqueConstraint(
                fields=["make", "name", "serial_number"], name="unique_lens"
            ),
        ]
        verbose_name_plural = "lenses"

    def __str__(self):
        return f"{self.make} {self.name} {self.serial_number}"
