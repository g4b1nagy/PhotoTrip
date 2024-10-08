import json

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _

from utils.admin import DATETIME_FORMAT, BaseModelAdmin, ReadOnlyModelAdmin
from utils.formatting import bytes_to_human_readable
from .models import Photo, FileType, MimeType, Camera, Lens


@admin.register(Photo)
class PhotoAdmin(BaseModelAdmin, ReadOnlyModelAdmin):
    search_fields = [
        "file_name",
    ]
    list_display = [
        "file_name",
        "taken_on_display",
        "file_size_display",
    ]
    list_filter = [
        "file_type",
        "mime_type",
        "camera",
        "lens",
    ]
    fieldsets = [
        [
            None,
            {
                "fields": [
                    "created_on_display",
                    "updated_on_display",
                ],
            },
        ],
        [
            "File system",
            {
                "fields": [
                    "thumbnail_display",
                    "file_name_display",
                    "file_path_display",
                    "is_image",
                    "is_video",
                    "file_size_display",
                    "file_atime_display",
                    "file_mtime_display",
                    "file_ctime_display",
                ],
            },
        ],
        [
            "Metadata",
            {
                "fields": [
                    "file_type",
                    "mime_type",
                    "image_width",
                    "image_height",
                    "megapixels",
                    "taken_on_display",
                    "gps_latitude",
                    "gps_longitude",
                    "gps_altitude",
                    "camera",
                    "lens",
                    "metadata_display",
                ],
            },
        ],
    ]

    @admin.display(
        description=_("Thumbnail"),
    )
    def thumbnail_display(self, obj):
        if obj.thumbnail.name == "":
            url = ""
        else:
            url = obj.thumbnail.url
        return format_html('<img src="{}">', url)

    @admin.display(
        description=_("File name"),
        ordering="file_name",
    )
    def file_name_display(self, obj):
        return format_html("<pre>{}</pre>", obj.file_name)

    @admin.display(
        description=_("File path"),
        ordering="file_path",
    )
    def file_path_display(self, obj):
        return format_html("<pre>{}</pre>", obj.file_path)

    @admin.display(
        description=_("File size"),
        ordering="file_size",
    )
    def file_size_display(self, obj):
        return bytes_to_human_readable(obj.file_size)

    @admin.display(
        description=_("File atime"),
        ordering="file_atime",
    )
    def file_atime_display(self, obj):
        return obj.file_atime.strftime(DATETIME_FORMAT)

    @admin.display(
        description=_("File mtime"),
        ordering="file_mtime",
    )
    def file_mtime_display(self, obj):
        return obj.file_mtime.strftime(DATETIME_FORMAT)

    @admin.display(
        description=_("File ctime"),
        ordering="file_ctime",
    )
    def file_ctime_display(self, obj):
        return obj.file_ctime.strftime(DATETIME_FORMAT)

    @admin.display(
        description=_("Taken on"),
        ordering="taken_on",
    )
    def taken_on_display(self, obj):
        if obj.taken_on is not None:
            return obj.taken_on.strftime(DATETIME_FORMAT)
        else:
            return ""

    @admin.display(
        description=_("Metadata"),
    )
    def metadata_display(self, obj):
        return format_html(
            "<pre>{}</pre>",
            json.dumps(obj.metadata, indent=4, sort_keys=True),
        )


@admin.register(FileType)
class FileTypeAdmin(BaseModelAdmin, ReadOnlyModelAdmin):
    search_fields = [
        "name",
    ]
    ordering = [
        "name",
    ]
    list_display = [
        "name",
    ]
    readonly_fields = [
        "created_on_display",
        "updated_on_display",
        "name",
        "matching_photos",
    ]

    @admin.display(
        description=_("Photos"),
    )
    def matching_photos(self, obj):
        url = reverse("admin:photos_photo_changelist")
        url = f"{url}?file_type__id__exact={obj.id}"
        text = _("matching photos")
        return format_html('<a href="{}">{}</a>', url, text)


@admin.register(MimeType)
class MimeTypeAdmin(BaseModelAdmin, ReadOnlyModelAdmin):
    search_fields = [
        "name",
    ]
    ordering = [
        "name",
    ]
    list_display = [
        "name",
    ]
    readonly_fields = [
        "created_on_display",
        "updated_on_display",
        "name",
        "matching_photos",
    ]

    @admin.display(
        description=_("Photos"),
    )
    def matching_photos(self, obj):
        url = reverse("admin:photos_photo_changelist")
        url = f"{url}?mime_type__id__exact={obj.id}"
        text = _("matching photos")
        return format_html('<a href="{}">{}</a>', url, text)


@admin.register(Camera)
class CameraAdmin(BaseModelAdmin, ReadOnlyModelAdmin):
    search_fields = [
        "make",
        "model",
    ]
    ordering = [
        "make",
        "model",
    ]
    list_display = [
        "make",
        "model",
    ]
    list_filter = [
        "make",
    ]
    readonly_fields = [
        "created_on_display",
        "updated_on_display",
        "make",
        "model",
        "matching_photos",
    ]

    @admin.display(
        description=_("Photos"),
    )
    def matching_photos(self, obj):
        url = reverse("admin:photos_photo_changelist")
        url = f"{url}?camera__id__exact={obj.id}"
        text = _("matching photos")
        return format_html('<a href="{}">{}</a>', url, text)


@admin.register(Lens)
class LensAdmin(BaseModelAdmin, ReadOnlyModelAdmin):
    search_fields = [
        "make",
        "model",
    ]
    ordering = [
        "make",
        "model",
    ]
    list_display = [
        "make",
        "model",
        "position",
    ]
    list_filter = [
        "make",
        "position",
    ]
    readonly_fields = [
        "created_on_display",
        "updated_on_display",
        "make",
        "model",
        "position",
        "matching_photos",
    ]

    @admin.display(
        description=_("Photos"),
    )
    def matching_photos(self, obj):
        url = reverse("admin:photos_photo_changelist")
        url = f"{url}?lens__id__exact={obj.id}"
        text = _("matching photos")
        return format_html('<a href="{}">{}</a>', url, text)
