from utils.models import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import pre_save


class Photo(BaseModel):
    thumbnail = models.FileField()
    file_name = models.CharField(max_length=256)
    file_path = models.CharField(max_length=4096)
    is_image = models.BooleanField(null=True)
    is_video = models.BooleanField(null=True)

    # Fields derived from os.stat():
    file_size = models.PositiveBigIntegerField()
    file_atime = models.DateTimeField()
    file_mtime = models.DateTimeField()
    file_ctime = models.DateTimeField()

    # Fields derived from utils.exif:
    file_type = models.ForeignKey("FileType", on_delete=models.PROTECT)
    mime_type = models.ForeignKey("MimeType", on_delete=models.PROTECT)
    image_width = models.PositiveIntegerField(null=True)
    image_height = models.PositiveIntegerField(null=True)
    megapixels = models.FloatField(null=True)
    taken_on = models.DateTimeField(null=True)
    gps_latitude = models.FloatField(null=True)
    gps_longitude = models.FloatField(null=True)
    gps_altitude = models.FloatField(null=True)
    camera = models.ForeignKey("Camera", null=True, on_delete=models.PROTECT)
    lens = models.ForeignKey("Lens", null=True, on_delete=models.PROTECT)
    metadata = models.JSONField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["file_path"], name="unique_photo_file_path"
            ),
        ]

    def __str__(self):
        return self.file_name


@receiver(pre_save, sender=Photo)
def photo_pre_save(sender, instance, *args, **kwargs):
    if instance.mime_type.name.startswith("image/"):
        instance.is_image = True
    elif instance.mime_type.name.startswith("video/"):
        instance.is_video = True


class FileType(BaseModel):
    name = models.CharField(max_length=128)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_file_type"),
        ]

    def __str__(self):
        return self.name


class MimeType(BaseModel):
    name = models.CharField(max_length=128)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_mime_type"),
        ]

    def __str__(self):
        return self.name


class Camera(BaseModel):
    make = models.CharField(max_length=128)
    model = models.CharField(max_length=128)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(make="") | ~models.Q(model=""),
                name="non_empty_camera",
            ),
            models.UniqueConstraint(fields=["make", "model"], name="unique_camera"),
        ]

    def __str__(self):
        return f"{self.make} {self.model}".strip()


class Lens(BaseModel):
    class Position(models.IntegerChoices):
        BACK = 0, _("back camera")
        FRONT = 1, _("front camera")

    make = models.CharField(max_length=128)
    model = models.CharField(max_length=128)
    position = models.IntegerField(choices=Position, null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(make="") | ~models.Q(model=""),
                name="non_empty_lens",
            ),
            models.UniqueConstraint(fields=["make", "model"], name="unique_lens"),
        ]
        verbose_name_plural = "lenses"

    def __str__(self):
        return f"{self.make} {self.model}".strip()


@receiver(pre_save, sender=Lens)
def lens_pre_save(sender, instance, *args, **kwargs):
    if " back " in instance.model:
        instance.position = Lens.Position.BACK
    elif " front " in instance.model:
        instance.position = Lens.Position.FRONT
