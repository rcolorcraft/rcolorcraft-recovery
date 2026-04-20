from django.db import models
from cloudinary.models import CloudinaryField


class ServiceImage(models.Model):
    image_name = models.CharField(max_length=255)
    image = CloudinaryField("image")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    type_of_art = models.CharField(max_length=100)
    userupload_id = models.IntegerField(default=0)

    is_verified_pic = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image_name
