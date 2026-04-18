from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
import shutil
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Employee
import re, random
import json
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

CustomUser = get_user_model()
# from .models import User
from django.contrib.auth.hashers import make_password
import os
import random
import re
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.db import transaction

from .models import Employee

from .models import Customer

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
import os
from django.conf import settings

TEMP_DIR = os.path.join(settings.MEDIA_ROOT, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import random, re


def save_customer_signup(request):
    if request.method == "POST":
        try:
            full_name = request.POST.get("customer_full_name")
            mobile = request.POST.get("mobile")
            email = request.POST.get("email")
            password = request.POST.get("customer_password")

            if not email:
                return JsonResponse({"success": False, "error": "Email is required!"})

            # ✅ Email validation
            email_regex = r"^[^@\s]+@[^\s@]+\.[^@\s]+$"
            if not re.match(email_regex, email):
                return JsonResponse({"success": False, "error": "Invalid email format"})

            # 🔥 ALWAYS GENERATE NEW OTP (IMPORTANT FIX)
            otp = str(random.randint(100000, 999999))

            print("🔥 Generated OTP:", otp)

            # ✅ SAVE SESSION (MATCH VERIFY FUNCTION)
            request.session["customer_otp"] = otp
            request.session["customer_signup_data"] = {
                "full_name": full_name,
                "mobile": mobile,
                "email_address": email,
                "password": password,
            }

            # ✅ force save
            request.session.modified = True

            print("📦 Session keys:", list(request.session.keys()))

            # ✅ Send OTP email
            send_mail(
                subject="OTP Verification - Rcolorcraft",
                message=f"""
            # Dear {full_name},

            # 🎨 Welcome to Rcolorcraft!

            # We're delighted to have you join us as a valued Customer.

            # To complete your registration, please verify your email address using the One-Time Password (OTP) below:

            # ━━━━━━━━━━━━━━━━━━━
            # 🔐 OTP: {otp}
            # ━━━━━━━━━━━━━━━━━━━

            # ⏳ This OTP is valid for the next 2 minutes.
            # ⚠️ For your security, please do not share this OTP with anyone.

            # Once verified, you'll be able to:
            # ✔ Explore professional painting services
            # ✔ Book trusted artists easily
            # ✔ Manage your bookings and projects seamlessly

            # If you did not request this signup, you can safely ignore this email.

            # Best regards,
            # * RColorCraftTeam *
            # 📧 info@rcolorcraft.com
            # """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            return JsonResponse({"success": True, "message": "OTP sent to your email!"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})


# from django.http import JsonResponse


def verify_customer_otp(request):
    if request.method == "POST":
        try:
            otp_entered = str(request.POST.get("otp")).strip()
            otp_saved = str(request.session.get("customer_otp", "")).strip()
            signup_data = request.session.get("customer_signup_data")

            print("🔢 Entered OTP:", otp_entered)
            print("💾 Saved OTP:", otp_saved)
            print("📦 Session keys:", list(request.session.keys()))

            # ❗ Session check
            if not otp_saved or not signup_data:
                return JsonResponse({"success": False, "error": "Session expired"})

            # ❗ OTP check
            if otp_entered != otp_saved:
                return JsonResponse({"success": False, "error": "Invalid OTP ❌"})

            email = signup_data["email_address"]

            # ✅ Duplicate check
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse(
                    {"success": False, "error": "Email already registered"}
                )

            # ✅ Create user
            user = CustomUser.objects.create_user(
                email=email,
                password=signup_data["password"],
                full_name=signup_data["full_name"],
                role="customer",
                is_verified=True,
            )

            # ✅ Create profile
            Customer.objects.create(
                user=user,
                mobile=signup_data.get("mobile"),
                email=email,
            )

            # ✅ Clear session AFTER success
            for key in ["customer_otp", "customer_signup_data"]:
                request.session.pop(key, None)

            return JsonResponse(
                {"success": True, "message": "Customer registered successfully!"}
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})


@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse AJAX JSON
            email = data.get("email")
            password = data.get("password")

            from django.contrib.auth import authenticate, login

            user = authenticate(request, email=email, password=password)

            if user is None:
                return JsonResponse(
                    {"success": False, "error": "Invalid email or password"}
                )

            if not user.is_verified:
                return JsonResponse(
                    {"success": False, "error": "Email not verified yet!"}
                )

            # Login and save session
            login(request, user)

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return render(request, "accounts/login.html")


@csrf_exempt
def login_auth(request):
    if request.method == "POST":
        try:
            email = request.POST.get("email")
            password = request.POST.get("password")

            from django.contrib.auth import authenticate, login

            user = authenticate(request, email=email, password=password)

            if user is None:
                return JsonResponse(
                    {"success": False, "error": "Invalid email or password"}
                )

            if not user.is_verified:
                return JsonResponse(
                    {"success": False, "error": "Email not verified yet!"}
                )

            # -------------------------------
            # 🔥 BLOCK CHECK FOR EMPLOYEE
            # -------------------------------
            if user.role == "employee":
                try:
                    employee = Employee.objects.get(user=user)

                    if employee.block_status:
                        return JsonResponse(
                            {
                                "success": False,
                                "error": "You are blocked by the Company Admin. Kindly contact +91-9759013133 or info@colorcraft.com for further information.",
                            }
                        )

                except Employee.DoesNotExist:
                    return JsonResponse(
                        {"success": False, "error": "Employee profile not found"}
                    )
            # -------------------------------

            # Login and save session
            login(request, user)

            # Role = Employee → Profile completion check
            if user.role == "employee":
                employee = Employee.objects.get(user=user)
                if (
                    not employee.fathers_name
                    or not employee.dob
                    or not employee.aadhar_card_no
                    or not employee.passport_photo
                ):

                    return JsonResponse(
                        {
                            "success": True,
                            "redirect_url": "/edit_profile/",
                            "message": "Please complete your profile to start working",
                        }
                    )

                return JsonResponse({"success": True, "redirect_url": "/"})

            # Other roles
            return JsonResponse({"success": True, "redirect_url": "/"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "accounts/login.html"
    success_url = reverse_lazy("accounts:login")  # Redirect after successful login

    def form_valid(self, form):
        messages.success(self.request, "Welcome back!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid email or password.")
        return super().form_invalid(form)


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/signup_employee.html"
    success_url = reverse_lazy("accounts:login")  # Redirect after signup

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, "Account created successfully! Please login.")
        return super().form_valid(form)  # use super() to respect success_url

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:login")


from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import random, re, os

# ❌ csrf_exempt हटाया (session issue avoid करने के लिए)


def save_employee_signup(request):
    if request.method == "POST":
        try:
            email = request.POST.get("email_address")
            full_name = request.POST.get("full_name")

            print("📩 Email:", email)
            print("👤 Name:", full_name)

            # ✅ Email validation
            if email:
                email_regex = r"^[^@\s]+@[^\s@]+\.[^@\s]+$"
                if not re.match(email_regex, email):
                    return JsonResponse(
                        {"success": False, "error": "Invalid email format"}
                    )

            # 🔥 OTP generate
            otp = str(random.randint(100000, 999999))

            # 🔥 Session में save (MOST IMPORTANT)
            request.session["employee_otp"] = otp
            request.session["employee_email"] = email

            print("✅ Generated OTP:", otp)
            print("✅ Saved OTP in session:", request.session.get("employee_otp"))

            # ✅ Form data save
            signup_data = request.POST.dict()
            request.session["employee_signup_data"] = signup_data

            # ✅ File save
            file_paths = {}
            fs = FileSystemStorage(location=TEMP_DIR)

            for field_name in [
                "aadhar_card_image_front",
                "aadhar_card_image_back",
                "passport_photo",
            ]:
                if field_name in request.FILES:
                    file_obj = request.FILES[field_name]
                    filename = fs.save(file_obj.name, file_obj)
                    file_paths[field_name] = os.path.join("temp", filename)

            request.session["employee_file_data"] = file_paths

            # 🔥 Email send
            send_mail(
                subject="🎨 Verify Your Email - Artist Signup | Rcolorcraft",
                message=f"""

                Dear {full_name},

🎨 Welcome to Rcolorcraft!

We're excited to have you join our platform as an Artist.

To complete your registration, please verify your email using the One-Time Password (OTP) below:

🔐 OTP: {otp}

⏳ This OTP is valid for the next 2 minutes.
⚠️ Please do not share this code with anyone for security reasons.

Once verified, you'll be able to showcase your creativity, connect with clients, and grow with us.

If you did not request this signup, please ignore this email.

Warm regards,  
* RcolorcraftTeam * 
📧 info@rcolorcraft.com
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            return JsonResponse({"success": True, "message": "OTP sent successfully"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})


from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.db import transaction
import os, shutil


def verify_employee_otp(request):
    if request.method == "POST":
        try:
            otp_entered = request.POST.get("otp")
            otp_saved = request.session.get("employee_otp")
            signup_data = request.session.get("employee_signup_data")
            file_data = request.session.get("employee_file_data")

            print("🔢 Entered OTP:", otp_entered)
            print("💾 Saved OTP:", otp_saved)

            # ✅ SIMPLE OTP CHECK (IMPORTANT FIX)
            if str(otp_entered).strip() != str(otp_saved).strip():
                return JsonResponse({"success": False, "error": "Invalid OTP"})

            if not signup_data:
                return JsonResponse({"success": False, "error": "Signup data missing"})

            try:
                final_paths = {}
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)

                # ✅ Files move
                for field_name, temp_rel_path in (file_data or {}).items():
                    temp_abs_path = os.path.join(settings.MEDIA_ROOT, temp_rel_path)
                    if os.path.exists(temp_abs_path):
                        final_path = os.path.join(
                            settings.MEDIA_ROOT, os.path.basename(temp_abs_path)
                        )
                        shutil.move(temp_abs_path, final_path)
                        final_paths[field_name] = os.path.basename(final_path)

                # ✅ DB save
                with transaction.atomic():

                    # duplicate check
                    if CustomUser.objects.filter(
                        email=signup_data["email_address"]
                    ).exists():
                        return JsonResponse(
                            {"success": False, "error": "Email already registered"}
                        )

                    # user create
                    user = CustomUser.objects.create_user(
                        email=signup_data["email_address"],
                        password=signup_data["password"],
                        full_name=signup_data["full_name"],
                        role="employee",
                        is_verified=True,
                    )

                    # employee create
                    Employee.objects.create(
                        user=user,
                        full_name=signup_data.get("full_name"),
                        mobile=signup_data.get("mobile"),
                        email_address=signup_data.get("email_address"),
                    )

                # ✅ session clear
                for key in [
                    "employee_otp",
                    "employee_signup_data",
                    "employee_file_data",
                ]:
                    request.session.pop(key, None)

                return JsonResponse(
                    {"success": True, "message": "Employee registered successfully!"}
                )

            except Exception as e:
                return JsonResponse(
                    {"success": False, "error": f"Error during signup: {str(e)}"}
                )

        except Exception as e:
            return JsonResponse({"success": False, "error": f"Server error: {str(e)}"})

    return JsonResponse({"success": False, "error": "Invalid request method"})


def signup_customer(request):
    if request.method == "POST":
        try:
            full_name = request.POST.get("customer_full_name")

            # ✅ VALIDATION
            if not full_name or full_name.strip() == "":
                return JsonResponse(
                    {"success": False, "error": "Full Name is required"}
                )

            # 👉 baaki signup logic
            return JsonResponse(
                {"success": True, "message": "Customer registered successfully"}
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return render(request, "accounts/signup_customer.html")


def signup_employee(request):
    return render(request, "accounts/signup_employee.html")


from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail


@csrf_exempt
def password_reset_ajax(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = CustomUser.objects.get(email=email)  # ✅ use CustomUser here
        except CustomUser.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "No account found with this email."}
            )

        # Generate reset token & link
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = request.build_absolute_uri(f"/accounts/reset/{uid}/{token}/")

        # Send email
        send_mail(
            subject="Password Reset Request",
            message=f"Click the link below to reset your password:\n\n{reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request"})


from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("password")
            user.set_password(new_password)
            user.save()
            return JsonResponse(
                {"success": True, "message": "Password reset successful!"}
            )

        # Valid link → show form
        return render(
            request,
            "password_reset.html",
            {"validlink": True, "uidb64": uidb64, "token": token},
        )
    else:
        # Invalid link → show error
        return render(request, "password_reset.html", {"validlink": False})


from django.contrib.auth.decorators import login_required


@login_required
def edit_profile(request):
    employee = Employee.objects.get(user=request.user)

    if request.method == "POST":

        employee.full_name = request.POST.get("full_name")
    employee.fathers_name = request.POST.get("fathers_name")
    employee.dob = request.POST.get("dob")
    employee.gender = request.POST.get("gender")

    employee.state = request.POST.get("state")
    employee.pincode = request.POST.get("pincode")
    employee.full_address = request.POST.get("full_address")

    employee.aadhar_card_no = request.POST.get("aadhar_card_no")

    employee.type_of_work = ",".join(request.POST.getlist("type_of_work"))

    employee.experience = request.POST.get("experience")
    employee.working_range = request.POST.get("working_range")

    employee.pan_card = request.POST.get("pan_card")
    employee.gst_no = request.POST.get("gst_no")
    employee.organization_name = request.POST.get("organization_name")

    employee.account_no = request.POST.get("account_no")
    employee.ifsc_code = request.POST.get("ifsc_code")
    employee.bank_account_holder_name = request.POST.get("bank_account_holder_name")

    # ✅ FILES FIX
    if request.FILES.get("aadhar_card_image_front"):
        employee.aadhar_card_image_front = request.FILES.get("aadhar_card_image_front")

    if request.FILES.get("aadhar_card_image_back"):
        employee.aadhar_card_image_back = request.FILES.get("aadhar_card_image_back")

    if request.FILES.get("passport_photo"):
        employee.passport_photo = request.FILES.get("passport_photo")

        employee.save()
    print("✅ Saved Successfully")

    return redirect("edit_profile")

    return render(request, "edit_profile.html", {"employee": employee})
