from django.contrib import admin
from django.utils.translation import gettext as _


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %z"


class BaseModelAdmin(admin.ModelAdmin):
    # Show most recent objects first
    ordering = ["-id"]

    # The default value is "-"
    empty_value_display = ""

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)

        # Make all list_display fields clickable
        self.list_display_links = self.list_display

    @admin.display(
        description=_("Created on"),
        ordering="created_on",
    )
    def created_on_display(self, obj):
        return obj.created_on.strftime(DATETIME_FORMAT)

    @admin.display(
        description=_("Updated on"),
        ordering="updated_on",
    )
    def updated_on_display(self, obj):
        return obj.updated_on.strftime(DATETIME_FORMAT)


class ReadOnlyModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
