from django.contrib import admin
from django.utils.html import format_html
from .models import ServiceImage  # ✅ same app → .models


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ("id", "image_name", "status_badge", "created_at")
    list_filter = ("is_approved",)

    def status_badge(self, obj):
        if obj.is_approved:
            return format_html('<span style="color:green;">● Live</span>')
        elif obj.is_verified_pic:
            return format_html('<span style="color:orange;">● Approved</span>')
        else:
            return format_html('<span style="color:red;">● Pending</span>')
