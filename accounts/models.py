from django.db import models
from django.conf import settings


# accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # hash password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    full_name = models.CharField(max_length=200, blank=True, null=True)
    role = models.CharField(max_length=50, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employees",
        null=True,
        blank=True,
    )
    full_name = models.CharField(max_length=150, null=True, blank=True)
    fathers_name = models.CharField(max_length=150, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)

    gender = models.CharField(max_length=20, null=True, blank=True)

    mobile = models.CharField(max_length=15, unique=True, null=True, blank=True)
    email_address = models.EmailField(unique=True, null=True, blank=True)

    house_no = models.CharField(max_length=50, null=True, blank=True)
    village = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)

    aadhar_card_no = models.CharField(max_length=12, unique=True, null=True, blank=True)
    aadhar_card_image_front = models.ImageField(
        upload_to="aadhar_cards/front/", null=True, blank=True
    )
    aadhar_card_image_back = models.ImageField(
        upload_to="aadhar_cards/back/", null=True, blank=True
    )

    # Extra fields
    experience = models.PositiveIntegerField(
        null=True, blank=True, help_text="Experience in years"
    )
    type_of_work = models.CharField(max_length=100, null=True, blank=True)
    preferred_work_location = models.CharField(max_length=100, null=True, blank=True)
    passport_photo = models.ImageField(
        upload_to="passport_photos/", null=True, blank=True
    )

    bank_account_holder_name = models.CharField(max_length=150, null=True, blank=True)
    account_no = models.BigIntegerField(unique=True, null=True, blank=True)
    ifsc_code = models.CharField(max_length=15, null=True, blank=True)

    full_address = models.TextField(null=True, blank=True)
    working_range = models.CharField(max_length=50, null=True, blank=True)
    belong_to_org = models.BooleanField(default=False)

    # New optional fields
    pan_card = models.CharField(
        max_length=10, null=True, blank=True, help_text="PAN Card Number"
    )
    gst_no = models.CharField(
        max_length=15, null=True, blank=True, help_text="GST Number"
    )
    organization_name = models.CharField(
        max_length=200, null=True, blank=True, help_text="Organization/Company Name"
    )

    password = models.CharField(max_length=128, null=True, blank=True)
    role = models.CharField(max_length=50, null=True, blank=True)
    status = models.BooleanField(default=False)
    block_status = models.BooleanField(default=False)

    class Meta:
        db_table = "Employee"

    def __str__(self):
        return self.full_name or "Unnamed Person"


class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customers",
        null=True,
        blank=True,
    )
    customer_full_name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    customer_password = models.CharField(max_length=128)
    customer_photo = models.ImageField(
        upload_to="customer_photos/", blank=True, null=True
    )
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = "customer"

    def __str__(self):
        return self.customer_full_name
