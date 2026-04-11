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


@csrf_exempt
def save_customer_signup(request):
    if request.method == "POST":
        try:
            full_name = request.POST.get("customer_full_name")
            mobile = request.POST.get("mobile")
            email = request.POST.get("email")
            create_password = request.POST.get("customer_password")

            if not email:
                return JsonResponse({"success": False, "error": "Email is required!"})

            # ✅ Email validation
            email_regex = r"^[^@\s]+@[^\s@]+\.[^@\s]+$"
            if not re.match(email_regex, email):
                return JsonResponse({"success": False, "error": "Invalid email format"})

            # 🔥 FIX: OTP only generate once
            if not request.session.get("otp"):
                otp = str(random.randint(100000, 999999))
                request.session["otp"] = otp
            else:
                otp = request.session.get("otp")

            print("Generated OTP:", otp)

            # ✅ Save data
            request.session["signup_data"] = {
                "customer_full_name": full_name,
                "mobile": mobile,
                "email": email,
                "customer_password": create_password,
            }

            request.session.modified = True

            send_mail(
                subject="OTP Verification",
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
            # ** RColorCraftTeam **
            # 📧 info@rcolorcraft.com
            # """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            return JsonResponse({"success": True, "message": "OTP sent"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})


# 🔥 VERIFY OTP CLEAN VERSION
@csrf_exempt
def verify_customer_otp(request):
    if request.method == "POST":
        try:
            otp_entered = str(request.POST.get("otp")).strip()
            otp_saved = str(request.session.get("otp", "")).strip()
            signup_data = request.session.get("signup_data")

            print("Entered OTP:", otp_entered)
            print("Saved OTP:", otp_saved)

            if not otp_saved or not signup_data:
                return JsonResponse({"success": False, "error": "Session expired"})

            if otp_entered != otp_saved:
                return JsonResponse({"success": False, "error": "Invalid OTP ❌"})

            email = signup_data["email"]

            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Email already registered. Please login.",
                    }
                )

            user = CustomUser.objects.create_user(
                email=email,
                password=signup_data["customer_password"],
                full_name=signup_data["customer_full_name"],
                role="customer",
                is_verified=True,
            )

            Customer.objects.create(
                user=user,
                mobile=signup_data["mobile"],
                email=email,
            )

            # ✅ clear session
            request.session.pop("otp", None)
            request.session.pop("signup_data", None)

            return JsonResponse(
                {"success": True, "message": "Account created successfully"}
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


@csrf_exempt
def save_employee_signup(request):
    if request.method == "POST":
        try:
            email = request.POST.get("email_address")
            full_name = request.POST.get("full_name")

            print(f"[DEBUG] Employee Signup - Email: {email}")
            print(f"[DEBUG] Employee Signup - Full Name: {full_name}")
            print(f"[DEBUG] Employee Signup - POST data: {request.POST.dict()}")

            if email:
                email_regex = r"^[^@\s]+@[^\s@]+\.[^@\s]+$"
                print(f"[DEBUG] Validating email: '{email}' with regex: {email_regex}")
                if not re.match(email_regex, email):
                    print(f"[DEBUG] Email validation FAILED for: {email}")
                    return JsonResponse(
                        {"success": False, "error": "Invalid email format"}
                    )
                print(f"[DEBUG] Email validation PASSED for: {email}")

            # Generate OTP
            otp = str(random.randint(100000, 999999))

            # Save form fields in session
            signup_data = request.POST.dict()
            request.session["employee_signup_data"] = signup_data
            request.session["employee_otp"] = otp

            # Save uploaded files to temp folder
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

            # Send OTP via email
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
** RcolorcraftTeam ** 
📧 info@rcolorcraft.com
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            return JsonResponse({"success": True, "message": "OTP sent to your email!"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})


@csrf_exempt
def verify_employee_otp(request):
    if request.method == "POST":
        try:
            otp_entered = request.POST.get("otp")
            otp_saved = request.session.get("employee_otp")
            signup_data = request.session.get("employee_signup_data")
            file_data = request.session.get("employee_file_data")

            print("OTP Entered:", otp_entered)
            print("OTP Saved in Session:", otp_saved)
            print("Session Keys:", list(request.session.keys()))

            # ✅ OTP validation
            if not (
                otp_entered
                and otp_saved
                and otp_entered.strip() == str(otp_saved).strip()
            ):
                return JsonResponse({"success": False, "error": "Invalid OTP"})

            if not signup_data:
                return JsonResponse(
                    {"success": False, "error": "Signup data missing in session"}
                )

            try:
                final_paths = {}
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)

                # ✅ Process uploaded files
                for field_name, temp_rel_path in (file_data or {}).items():
                    temp_abs_path = os.path.join(settings.MEDIA_ROOT, temp_rel_path)
                    if os.path.exists(temp_abs_path):
                        final_path = os.path.join(
                            settings.MEDIA_ROOT, os.path.basename(temp_abs_path)
                        )
                        shutil.move(
                            temp_abs_path, final_path
                        )  # move instead of saving again
                        final_paths[field_name] = os.path.basename(final_path)

                # ✅ Database ops inside transaction
                with transaction.atomic():
                    # Check duplicate email
                    if CustomUser.objects.filter(
                        email=signup_data["email_address"]
                    ).exists():
                        return JsonResponse(
                            {"success": False, "error": "Email already registered"}
                        )

                    # 1. Create CustomUser
                    user = CustomUser.objects.create_user(
                        email=signup_data["email_address"],
                        password=signup_data["password"],
                        full_name=signup_data["full_name"],
                        role="employee",
                        is_verified=True,
                    )

                    # 2. Create Employee profile
                    employee = Employee.objects.create(
                        user=user,
                        full_name=signup_data.get("full_name"),
                        # fathers_name=signup_data.get('fathers_name'),
                        # dob=signup_data.get('dob'),
                        # gender=signup_data.get('gender'),
                        mobile=signup_data.get("mobile"),
                        email_address=signup_data.get("email_address"),
                        # house_no=signup_data.get('house_no'),
                        # village=signup_data.get('village'),
                        # city=signup_data.get('city'),
                        # state=signup_data.get('state'),
                        # pincode=signup_data.get('pincode'),
                        # aadhar_card_no=signup_data.get('aadhar_card_no'),
                        # experience=signup_data.get('experience'),
                        # type_of_work=signup_data.get('type_of_work', ''),
                        # preferred_work_location=signup_data.get('preferred_work_location'),
                        # bank_account_holder_name=signup_data.get('bank_account_holder_name'),
                        # account_no=signup_data.get('account_no'),
                        # ifsc_code=signup_data.get('ifsc_code'),
                        # aadhar_card_image_front=final_paths.get('aadhar_card_image_front'),
                        # aadhar_card_image_back=final_paths.get('aadhar_card_image_back'),
                        # passport_photo=final_paths.get('passport_photo'),
                    )

                # ✅ Clear only after success
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
