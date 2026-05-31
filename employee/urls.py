from django.urls import path
from . import views

urlpatterns = [
    path("service_images/", views.service_images_view, name="service_images"),
    path("pending-uploads/", views.pending_uploads_view, name="pending_uploads"),
]
