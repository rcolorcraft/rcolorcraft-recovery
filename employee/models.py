from django.db import models
from django.contrib.auth.models import User


class ServiceImage(models.Model):
    id = models.AutoField(primary_key=True)
    image_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    from cloudinary.models import CloudinaryField

    image = CloudinaryField("image")

    type_of_art = models.CharField(max_length=100)
    file_url = models.URLField(blank=True, null=True)
    userupload_id = models.IntegerField(
        default=0
    )  # if you just want to store an ID manually
    userupload_name = models.CharField(
        max_length=255, default="Anonymous", null=False, blank=False
    )  # uploader’s name as text
    is_verified_pic = models.BooleanField(default=False)
    min_size = models.CharField(
        max_length=50, default=""
    )  # <-- New field for '10 * 60'

    class Meta:
        db_table = "service_images"

    def __str__(self):
        return f"{self.image_name} ({self.type_of_art})"
