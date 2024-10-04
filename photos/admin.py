from django.contrib import admin

from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _
import json

from utils.formatting import bytes_to_human_readable
from utils.admin import BaseModelAdmin
from .models import Photo, FileType, MimeType, Camera, Lens


@admin.register(Photo)
class PhotoAdmin(BaseModelAdmin):
    search_fields = [
        "file_name",
    ]
    list_display = [
        "file_name",
        "file_size_formatted",
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
                    "created_on",
                    "updated_on",
                ],
            },
        ],
        [
            "File system",
            {
                "fields": [
                    "thumbnail_display",
                    "file_name_formatted",
                    "file_path_formatted",
                    "file_size_formatted",
                    "file_atime",
                    "file_mtime",
                    "file_ctime",
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
                    "taken_on",
                    "gps_latitude",
                    "gps_longitude",
                    "gps_altitude",
                    "camera",
                    "lens",
                    "metadata_formatted",
                ],
            },
        ],
    ]
    readonly_fields = [
        "created_on",
        "updated_on",
        "thumbnail_display",
        "file_name_formatted",
        "file_path_formatted",
        "file_size_formatted",
        "file_atime",
        "file_mtime",
        "file_ctime",
        "file_type",
        "mime_type",
        "image_width",
        "image_height",
        "megapixels",
        "taken_on",
        "gps_latitude",
        "gps_longitude",
        "gps_altitude",
        "camera",
        "lens",
        "metadata_formatted",
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
    )
    def file_name_formatted(self, obj):
        return format_html("<pre>{}</pre>", obj.file_name)

    @admin.display(
        description=_("File path"),
    )
    def file_path_formatted(self, obj):
        return format_html("<pre>{}</pre>", obj.file_path)

    @admin.display(
        ordering="file_size",
        description=_("File size"),
    )
    def file_size_formatted(self, obj):
        return bytes_to_human_readable(obj.file_size)

    @admin.display(
        description=_("Metadata"),
    )
    def metadata_formatted(self, obj):
        return format_html(
            "<pre>{}</pre>",
            json.dumps(obj.metadata, indent=4, sort_keys=True),
        )


@admin.register(FileType)
class FileTypeAdmin(BaseModelAdmin):
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
        "created_on",
        "updated_on",
        "name",
        "matching_photos",
    ]

    @admin.display(
        description=_("Photos"),
    )
    def matching_photos(self, obj):
        url = reverse("admin:photos_photo_changelist")
        url = f"{url}?file_type__id__exact={obj.id}"
        text = _("view matching photos")
        return format_html('<a href="{}">{}</a>', url, text)


@admin.register(MimeType)
class MimeTypeAdmin(BaseModelAdmin):
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
        "created_on",
        "updated_on",
        "name",
        "matching_photos",
    ]

    @admin.display(
        description=_("Photos"),
    )
    def matching_photos(self, obj):
        url = reverse("admin:photos_photo_changelist")
        url = f"{url}?mime_type__id__exact={obj.id}"
        text = _("view matching photos")
        return format_html('<a href="{}">{}</a>', url, text)


@admin.register(Camera)
class CameraAdmin(BaseModelAdmin):
    search_fields = [
        "make",
        "model",
        "serial_number",
    ]
    ordering = [
        "make",
        "model",
        "serial_number",
    ]
    list_display = [
        "make",
        "model",
        "serial_number",
    ]
    list_filter = [
        "make",
    ]
    readonly_fields = [
        "created_on",
        "updated_on",
        "make",
        "model",
        "serial_number",
        "matching_photos",
    ]

    @admin.display(
        description=_("Photos"),
    )
    def matching_photos(self, obj):
        url = reverse("admin:photos_photo_changelist")
        url = f"{url}?camera__id__exact={obj.id}"
        text = _("view matching photos")
        return format_html('<a href="{}">{}</a>', url, text)


@admin.register(Lens)
class LensAdmin(BaseModelAdmin):
    search_fields = [
        "make",
        "name",
        "serial_number",
    ]
    ordering = [
        # 'make',
        "name",
        "serial_number",
    ]
    list_display = [
        "make",
        "name",
        "serial_number",
    ]
    list_filter = [
        "make",
    ]
    readonly_fields = [
        "created_on",
        "updated_on",
        "make",
        "name",
        "serial_number",
        "matching_photos",
    ]

    @admin.display(
        description=_("Photos"),
    )
    def matching_photos(self, obj):
        url = reverse("admin:photos_photo_changelist")
        url = f"{url}?lens__id__exact={obj.id}"
        text = _("view matching photos")
        return format_html('<a href="{}">{}</a>', url, text)
