from django.contrib import admin
from .models import Employee
from django.utils.html import format_html


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "mobile", "status")

    def aadhar_front_preview(self, obj):
        if obj.aadhar_card_image_front:
            return format_html(
                '<img src="{}" width="100" />', obj.aadhar_card_image_front.url
            )
        return "No Image"

    def aadhar_back_preview(self, obj):
        if obj.aadhar_card_image_back:
            return format_html(
                '<img src="{}" width="100" />', obj.aadhar_card_image_back.url
            )
        return "No Image"

    readonly_fields = ("aadhar_front_preview", "aadhar_back_preview")
