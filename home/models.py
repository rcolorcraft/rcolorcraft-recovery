from django.db import models

from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


from django.db import models


class Assignment(models.Model):
    customer_name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    price = models.IntegerField()

    status = models.CharField(max_length=20, default="pending")
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.customer_name


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_process", "In Process"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    id = models.AutoField(primary_key=True)  # Primary key
    booking_id = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=100)
    customer_user_id = models.IntegerField()
    service_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    pin_code = models.CharField(max_length=10)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    total_walls = models.IntegerField()
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    total_sqft = models.DecimalField(max_digits=12, decimal_places=2)
    appointment_date = models.DateField()
    design_names = models.TextField(blank=True, null=True)
    type_of_art_booked = models.CharField(max_length=100)
    customer_design = models.ImageField(
        upload_to="customer_designs/", blank=True, null=True
    )
    price_of_design = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    # Payment-related fields
    payment_option = models.CharField(
        max_length=50, default="Razorpay"
    )  # free text field
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    ASSIGNMENT_STATUS_CHOICES = [
        ("assigned", "Assigned"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    ]

    assigned_employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_bookings",
    )
    assignment_status = models.CharField(
        max_length=20, choices=ASSIGNMENT_STATUS_CHOICES, default="assigned"
    )
    artist_status = models.BooleanField(default=False)
    customer_status = models.BooleanField(default=False)

    class Meta:
        db_table = "booking"

    def __str__(self):
        return f"{self.booking_id} - {self.service_name}"


from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):

    customer_id = models.CharField(max_length=50)

    customer_name = models.CharField(max_length=100)

    customer_email = models.EmailField()

    customer_review = models.TextField(blank=True, null=True)

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    review_image = models.ImageField(upload_to="reviews/", blank=True, null=True)

    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_name


# models.py
from django.db import models
from django.conf import settings


class CustomProduct(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    material = models.CharField(max_length=100, null=True, blank=True)
    other_material = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Custom Product ({self.user})"


from django.db import models
from django.conf import settings
import uuid


class BookingOrder(models.Model):
    # ✅ Primary key (automatically created as `id` by Django, but you can define explicitly)
    id = models.BigAutoField(primary_key=True)

    # ✅ External reference ID (useful for Razorpay or tracking)
    query_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="booking_orders",
    )
    product_name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=200, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} - ₹{self.amount} ({self.status})"

    class Meta:
        db_table = "booking_order"  # ✅ table name in pgAdmin
        verbose_name = "Booking Order"  # ✅ display name in Django admin
        verbose_name_plural = "Booking Orders"  # ✅ plural name in Django admin
        ordering = ["-created_at"]  # ✅ latest first


from django.db import models


class Consultation(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()

    def __str__(self):
        return self.name


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Artist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    status = models.BooleanField(default=False)  # LIVE control
    kyc_status = models.CharField(max_length=20, default="pending")  # KYC status
