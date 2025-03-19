from django.contrib import admin
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.utils.html import escape, format_html
from solo.admin import SingletonModelAdmin

from apps.home.models import SiteConfiguration


@admin.register(SiteConfiguration)
class ConfigAdmin(SingletonModelAdmin):
    readonly_fields = ("manifest_version",)


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = "action_time"

    readonly_fields = [f.name for f in LogEntry._meta.fields]

    list_filter = ["user", "content_type", "action_flag"]

    search_fields = ["object_repr", "change_message"]

    list_display = [
        "action_time",
        "user",
        "content_type",
        "object_link",
        "action_flag",
        "get_change_message",
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="object", ordering="object_repr")  # type: ignore [attr-defined]
    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            link = format_html('<a href="{}">{}</a>', obj.get_admin_url(), escape(obj.object_repr))
        return link

    @staticmethod
    def action_flag(obj):
        action_map = {
            DELETION: "Deletion",
            CHANGE: "Change",
            ADDITION: "Addition",
        }
        return action_map.get(obj.action_flag, obj.action_flag)
