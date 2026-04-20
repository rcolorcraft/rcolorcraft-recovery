from django.contrib import admin
from .models import ServiceImage


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ["id", "image_name", "is_approved"]
    list_editable = ["is_approved"]
