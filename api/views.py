from django.shortcuts import render

# Create your views here.
import random, re
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.models import CustomUser, Customer


@csrf_exempt
def save_customer_signup_api(request):
    if request.method == "POST":
        try:
            full_name = request.POST.get("customer_full_name")
            mobile = request.POST.get("mobile")
            email = request.POST.get("email")
            create_password = request.POST.get("customer_password")

            if not all([full_name, mobile, email, create_password]):
                return JsonResponse(
                    {"success": False, "error": "All fields are required"}
                )

            # Email validation
            email_regex = r"^[^@\s]+@[^\s@]+\.[^@\s]+$"
            if not re.match(email_regex, email):
                return JsonResponse({"success": False, "error": "Invalid email format"})

            # Generate OTP
            otp = str(random.randint(100000, 999999))

            # Save in session temporarily
            request.session["signup_data"] = {
                "customer_full_name": full_name,
                "mobile": mobile,
                "email": email,
                "customer_password": create_password,
            }
            request.session["otp"] = otp

            # Send OTP email
            send_mail(
                subject="🎨 Rcolorcraft - Customer Email Verification OTP",
                message=f"""
Dear {full_name},

Welcome to Rcolorcraft.. 🎨

Thank you for signing up as a customer.

Your One-Time Password (OTP) for account verification is:

🔐 OTP: {otp}

⏳ This OTP is valid for 2 minutes.
⚠️ Do not share this OTP with anyone.

If you did not request this, please ignore this email.

Warm Regards,  
 ** Rcolorcraft Team ** 
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
def verify_customer_otp_api(request):
    if request.method == "POST":
        otp_entered = request.POST.get("otp")
        otp_saved = request.session.get("otp")
        signup_data = request.session.get("signup_data")

        if otp_saved and signup_data and otp_entered == otp_saved:
            # Save user & customer after OTP verification
            user = CustomUser.objects.create_user(
                email=signup_data["email"],
                password=signup_data["customer_password"],
                full_name=signup_data["customer_full_name"],
                role="customer",
                is_verified=True,
            )

            Customer.objects.create(
                customer_full_name=signup_data["customer_full_name"],
                user=user,
                mobile=signup_data["mobile"],
                email=signup_data["email"],
                customer_password=signup_data["customer_password"],
                is_verified=True,
            )

            # Clear session
            del request.session["otp"]
            del request.session["signup_data"]

            return JsonResponse(
                {"success": True, "message": "Email verified & customer registered!"}
            )
        else:
            return JsonResponse({"success": False, "error": "Invalid OTP"})

    return JsonResponse({"success": False, "error": "Invalid request method"})


import random, re
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from accounts.models import CustomUser, Employee


import json
import jwt  # Required for token decoding
import time
from decimal import Decimal

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings

# JWT Imports
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings

# Model Imports (Assuming these are correct based on your files)
from accounts.models import Employee, Customer
from wallet.models import Wallet, WalletTransaction

# Get the custom User model for use in helper function
User = get_user_model()


# =====================================================================
# 1. TOKEN HELPER FUNCTION (REQUIRED for all secured APIs)
# =====================================================================
def get_user_from_token(request):
    """Decodes the JWT token from the Authorization header and returns the User object."""
    auth_header = request.headers.get("Authorization")

    # Check if header is present and starts with 'Bearer '
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, "Authentication credentials were not provided"

    # Extract the token (e.g., "Bearer token" -> "token")
    token = auth_header.split(" ")[1]

    try:
        # Decode and Validate the Token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[api_settings.ALGORITHM]
        )

        # Get the user ID from the token payload
        user_id = payload.get(api_settings.USER_ID_CLAIM)

        # Retrieve the user from the database
        user = User.objects.get(id=user_id)

        return user, None  # Success: return user and no error

    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.DecodeError:
        return None, "Invalid token"
    except User.DoesNotExist:
        return None, "User not found for token"
    except Exception as e:
        # Catch any other decoding/database errors
        return None, f"Authentication error: {str(e)}"


# =====================================================================
# 2. LOGIN API (Generates Token)
# =====================================================================


# Helper function to get tokens (using DRF Simple JWT logic)
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


@csrf_exempt
def login_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"})

    try:
        # Parse JSON data from Flutter (Assuming JSON body)
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        if not all([email, password]):
            return JsonResponse(
                {"success": False, "error": "Email and password are required"}
            )

        # Authenticate user
        user = authenticate(request, email=email, password=password)

        if user is None:
            return JsonResponse(
                {"success": False, "error": "Invalid email or password"}
            )

        if not user.is_verified:
            return JsonResponse({"success": False, "error": "Email not verified yet!"})

        # GENERATE JWT TOKENS
        tokens = get_tokens_for_user(user)

        user_data = {
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
        }

        # RETURN TOKENS IN THE RESPONSE
        return JsonResponse(
            {
                "success": True,
                "user": user_data,
                "token": tokens["access"],  # <-- Send the access token
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# =====================================================================
# 3. CUSTOMER PROFILE APIs (Uses Token)
# =====================================================================


@csrf_exempt
def api_get_customer_profile(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "error": "GET method required"})

    # 🚀 Authenticate user using the Authorization token
    user, error = get_user_from_token(request)
    if not user:
        return JsonResponse({"success": False, "error": error}, status=401)

    if user.role != "customer":
        return JsonResponse(
            {"success": False, "error": "Forbidden: Not a customer"}, status=403
        )

    try:
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Customer profile not found"}, status=404
        )

    return JsonResponse(
        {
            "success": True,
            "data": {
                "name": customer.customer_full_name,
                "email": customer.email,
                "mobile": customer.mobile,
                "profile_photo": (
                    customer.customer_photo.url if customer.customer_photo else None
                ),
            },
        }
    )


@csrf_exempt
def api_update_customer_profile(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required"})

    # 🚀 Authenticate user using the Authorization token
    user, error = get_user_from_token(request)
    if not user:
        return JsonResponse({"success": False, "error": error}, status=401)

    if user.role != "customer":
        return JsonResponse(
            {
                "success": False,
                "error": "Forbidden: Only customers can update this profile",
            },
            status=403,
        )

    try:
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Customer profile not found"}, status=404
        )

    # --- Original update logic ---
    customer.customer_full_name = request.POST.get("name")
    customer.email = request.POST.get("email")  # Assuming this is allowed
    customer.mobile = request.POST.get("mobile")  # Assuming this is allowed

    if "profile_photo" in request.FILES:
        customer.customer_photo = request.FILES["profile_photo"]
    # ... (rest of your update logic if any)

    customer.save()

    return JsonResponse({"success": True, "message": "Profile updated successfully"})


# =====================================================================
# 4. EMPLOYEE PROFILE APIs (Uses Token)
# =====================================================================


@csrf_exempt
def api_get_employee_profile(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "error": "GET method required"})

    # 🚀 Authenticate user using the token
    user, error = get_user_from_token(request)
    if not user:
        return JsonResponse({"success": False, "error": error}, status=401)

    if user.role != "employee":
        return JsonResponse(
            {"success": False, "error": "Forbidden: Not an employee"}, status=403
        )

    try:
        employee = Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Employee profile not found"}, status=404
        )

    return JsonResponse(
        {
            "success": True,
            "data": {
                "full_name": user.full_name,
                "email": user.email,  # read-only
                "mobile": employee.mobile,
                "father_name": employee.fathers_name,
                "dob": str(employee.dob),
                "gender": employee.gender,
                "house_no": employee.house_no,
                "village": employee.village,
                "city": employee.city,
                "state": employee.state,
                "pincode": employee.pincode,
                "aadhar_card_no": employee.aadhar_card_no,
                "experience": employee.experience,
                "preferred_work_location": employee.preferred_work_location,
                "type_of_work": employee.type_of_work,
                "ready_to_take_orders": employee.status,
                "passport_photo": (
                    employee.passport_photo.url if employee.passport_photo else None
                ),
                "aadhar_front": (
                    employee.aadhar_card_image_front.url
                    if employee.aadhar_card_image_front
                    else None
                ),
                "aadhar_back": (
                    employee.aadhar_card_image_back.url
                    if employee.aadhar_card_image_back
                    else None
                ),
            },
        }
    )


import jwt
import json
import time
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Assuming you have these models imported in your file
from accounts.models import Employee
from wallet.models import Wallet, WalletTransaction

# For JWT decoding
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth import get_user_model

User = get_user_model()


@csrf_exempt
def api_update_employee_profile(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required"})

    # 🚀 NEW: Authenticate user using the token
    user, error = get_user_from_token(request)
    if not user:
        return JsonResponse({"success": False, "error": error}, status=401)

    # 🚀 NEW: Check role after authentication
    if user.role != "employee":
        return JsonResponse(
            {"success": False, "error": "Forbidden: Not an employee"}, status=403
        )

    try:
        employee = Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Employee profile not found"}, status=404
        )

    full_name = request.POST.get("full_name")
    mobile = request.POST.get("mobile")

    if full_name:
        user.full_name = full_name
        user.save(update_fields=["full_name"])

    if mobile:
        employee.mobile = mobile

    prev_status = employee.status

    # Basic fields
    employee.fathers_name = request.POST.get("fathers_name")
    employee.dob = request.POST.get("dob")
    employee.gender = request.POST.get("gender")
    employee.house_no = request.POST.get("house_no")
    employee.village = request.POST.get("village")
    employee.city = request.POST.get("city")
    employee.state = request.POST.get("state")
    employee.pincode = request.POST.get("pincode")
    employee.aadhar_card_no = request.POST.get("aadhar_card_no")
    employee.experience = request.POST.get("experience")

    # Multi-Select
    # Note: request.POST.getlist works correctly for POST data
    employee.type_of_work = request.POST.get(
        "type_of_work"
    )  # Assuming you want a single string if it's not a list field
    employee.preferred_work_location = request.POST.get(
        "preferred_work_location"
    )  # Assuming this is a single string

    # Files
    if "passport_photo" in request.FILES:
        employee.passport_photo = request.FILES["passport_photo"]

    if "aadhar_front" in request.FILES:
        employee.aadhar_card_image_front = request.FILES["aadhar_front"]

    if "aadhar_back" in request.FILES:
        employee.aadhar_card_image_back = request.FILES["aadhar_back"]

    # Banking + org fields
    employee.bank_account_holder_name = request.POST.get("bank_account_holder_name")
    employee.account_no = request.POST.get("account_no") or None
    employee.ifsc_code = request.POST.get("ifsc_code")
    employee.pan_card = request.POST.get("pan_card")
    employee.gst_no = request.POST.get("gst_no")
    employee.organization_name = request.POST.get("organization_name")

    # Ready to take orders
    is_ready = request.POST.get("ready_to_take_orders") == "true"

    # Deduct ₹20 only ONCE
    if not prev_status and is_ready:
        # Assuming Wallet and WalletTransaction models are imported
        wallet = Wallet.objects.filter(user=user).first()

        if wallet and wallet.balance >= Decimal("20.00"):
            wallet.balance -= Decimal("20.00")
            wallet.save()

            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type="DEBIT",
                amount=Decimal("20.00"),
                razorpay_payment_id=f"ACTIVATION_{user.id}_{int(time.time())}",
            )

            employee.status = True
        else:
            employee.status = False
            employee.save()
            return JsonResponse(
                {"success": False, "message": "Insufficient wallet balance"}
            )

    else:
        employee.status = is_ready

    employee.save()

    return JsonResponse(
        {"success": True, "message": "Employee profile updated successfully"}
    )


# @csrf_exempt
# def api_get_employee_profile(request):
#     if request.method != "GET":
#         return JsonResponse({"success": False, "error": "GET method required"})

#     # 🚀 NEW: Authenticate user using the token
#     user, error = get_user_from_token(request)
#     if not user:
#         return JsonResponse({"success": False, "error": error}, status=401)

#     # 🚀 NEW: Check role after authentication
#     if user.role != "employee":
#         return JsonResponse({"success": False, "error": "Forbidden: Not an employee"}, status=403)

#     try:
#         employee = Employee.objects.get(user=user)
#     except Employee.DoesNotExist:
#         return JsonResponse({"success": False, "error": "Employee profile not found"}, status=404)

#     return JsonResponse({
#         "success": True,
#         "data": {
#             "father_name": employee.fathers_name,
#             "dob": str(employee.dob),
#             "gender": employee.gender,
#             "house_no": employee.house_no,
#             "village": employee.village,
#             "city": employee.city,
#             "state": employee.state,
#             "pincode": employee.pincode,
#             "aadhar_card_no": employee.aadhar_card_no,
#             "experience": employee.experience,
#             "preferred_work_location": employee.preferred_work_location,
#             "type_of_work": employee.type_of_work,
#             "ready_to_take_orders": employee.status,
#             "passport_photo": employee.passport_photo.url if employee.passport_photo else None,
#             "aadhar_front": employee.aadhar_card_image_front.url if employee.aadhar_card_image_front else None,
#             "aadhar_back": employee.aadhar_card_image_back.url if employee.aadhar_card_image_back else None,
#         }
#     })


@csrf_exempt
def save_employee_signup_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"})

    try:
        email = request.POST.get("email_address")
        full_name = request.POST.get("full_name")
        mobile = request.POST.get("mobile", "")

        if not all([email, full_name]):
            return JsonResponse(
                {"success": False, "error": "Email and full name are required"}
            )

        # Validate email
        email_regex = r"^[^@\s]+@[^\s@]+\.[^@\s]+$"
        if not re.match(email_regex, email):
            return JsonResponse({"success": False, "error": "Invalid email format"})

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Save form fields in session
        signup_data = {
            "full_name": full_name,
            "email_address": email,
            "mobile": mobile,
            "password": request.POST.get(
                "password", "defaultpass123"
            ),  # optional default password
        }
        request.session["employee_signup_data"] = signup_data
        request.session["employee_otp"] = otp

        # Send OTP via email
        send_mail(
            subject="🎨 Rcolorcraft - Employee Verification OTP",
            message=f"""
Dear {full_name},

Welcome to Rcolorcraft 🎨

Thank you for registering as a team member.

━━━━━━━━━━━━━━━━━━━━━━━

🔐 Your One-Time Password (OTP)

👉 {otp}

━━━━━━━━━━━━━━━━━━━━━━━

⏳ This OTP is valid for 2 minutes  
🔒 Please do not share this OTP with anyone

We are excited to have you on our team!

If you did not request this, please ignore this email.

━━━━━━━━━━━━━━━━━━━━━━━

Best Regards,  
** Rcolorcraft Team ** 
📧 info@rcolorcraft.com  
🌐 www.rcolorcraft.com
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return JsonResponse({"success": True, "message": "OTP sent to your email!"})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
def verify_employee_otp_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"})

    try:
        otp_entered = request.POST.get("otp")
        otp_saved = request.session.get("employee_otp")
        signup_data = request.session.get("employee_signup_data")

        # ✅ OTP validation
        if not (
            otp_entered and otp_saved and otp_entered.strip() == str(otp_saved).strip()
        ):
            return JsonResponse({"success": False, "error": "Invalid OTP"})

        if not signup_data:
            return JsonResponse(
                {"success": False, "error": "Signup data missing in session"}
            )

        # Database operations inside transaction
        with transaction.atomic():
            if CustomUser.objects.filter(email=signup_data["email_address"]).exists():
                return JsonResponse(
                    {"success": False, "error": "Email already registered"}
                )

            # 1. Create user
            user = CustomUser.objects.create_user(
                email=signup_data["email_address"],
                password=signup_data["password"],
                full_name=signup_data["full_name"],
                role="employee",
                is_verified=True,
            )

            # 2. Create employee profile
            Employee.objects.create(
                user=user,
                full_name=signup_data["full_name"],
                mobile=signup_data.get("mobile", ""),
                email_address=signup_data["email_address"],
            )

        # Clear session after success
        for key in ["employee_otp", "employee_signup_data"]:
            request.session.pop(key, None)

        return JsonResponse(
            {"success": True, "message": "Employee registered successfully!"}
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": f"Server error: {str(e)}"})


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.conf import settings
from wallet.models import Wallet, WalletTransaction

import razorpay
import json
import time
from decimal import Decimal

razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


# @csrf_exempt
# def api_create_order(request):
#     """REST API → Create Razorpay wallet recharge order"""
#     if request.method != "POST":
#         return JsonResponse({"success": False, "error": "POST method required"})

#     try:
#         body = json.loads(request.body)
#         amount = int(float(body.get("amount", 0)) * 100)

#         if amount < 100:
#             return JsonResponse({"success": False, "error": "Minimum amount is ₹1"})

#         receipt_id = f"wallet_{int(time.time())}"

#         order_data = {
#             "amount": amount,
#             "currency": "INR",
#             "receipt": receipt_id,
#             "payment_capture": 1
#         }

#         order = razorpay_client.order.create(order_data)

#         return JsonResponse({
#             "success": True,
#             "order_id": order["id"],
#             "amount": order["amount"],
#             "currency": order["currency"],
#             "key_id": settings.RAZORPAY_KEY_ID,
#         })

#     except Exception as e:
#         return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
def api_create_order(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST method required"})

    # 🚀 Authenticate
    user, error = get_user_from_token(request)
    if not user:
        return JsonResponse({"success": False, "error": error}, status=401)

    try:
        body = json.loads(request.body)
        amount = int(float(body.get("amount", 0)) * 100)

        if amount < 100:
            return JsonResponse({"success": False, "error": "Minimum amount is ₹1"})

        receipt_id = f"wallet_{int(time.time())}_{user.id}"

        order_data = {
            "amount": amount,
            "currency": "INR",
            "receipt": receipt_id,
            "payment_capture": 1,
        }

        order = razorpay_client.order.create(order_data)

        return JsonResponse(
            {
                "success": True,
                "order_id": order["id"],
                "amount": order["amount"],
                "currency": order["currency"],
                "key_id": settings.RAZORPAY_KEY_ID,
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# @csrf_exempt
# def api_verify_payment(request):
#     """REST API → Verify payment and credit wallet"""
#     if request.method != "POST":
#         return JsonResponse({"success": False, "error": "POST method required"})

#     try:
#         body = json.loads(request.body)

#         user_id = body.get("user_id")
#         if not user_id:
#             return JsonResponse({"success": False, "error": "user_id required"})

#         user = User.objects.get(id=user_id)

#         razorpay_order_id = body.get("razorpay_order_id")
#         razorpay_payment_id = body.get("razorpay_payment_id")
#         razorpay_signature = body.get("razorpay_signature")
#         amount = Decimal(str(body.get("amount")))

#         params_dict = {
#             "razorpay_order_id": razorpay_order_id,
#             "razorpay_payment_id": razorpay_payment_id,
#             "razorpay_signature": razorpay_signature
#         }

#         # verify payment signature
#         razorpay_client.utility.verify_payment_signature(params_dict)

#         # credit wallet
#         wallet, _ = Wallet.objects.get_or_create(user=user)
#         wallet.credit(amount)

#         WalletTransaction.objects.create(
#             wallet=wallet,
#             amount=amount,
#             transaction_type="CREDIT",
#             razorpay_payment_id=razorpay_payment_id
#         )

#         return JsonResponse({"success": True, "message": "Wallet credited successfully"})

#     except razorpay.errors.SignatureVerificationError:
#         return JsonResponse({"success": False, "error": "Signature verification failed"})

#     except Exception as e:
#         return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
def api_verify_payment(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST method required"})

    # 🚀 Authenticate user
    user, error = get_user_from_token(request)
    if not user:
        return JsonResponse({"success": False, "error": error}, status=401)

    try:
        body = json.loads(request.body)

        razorpay_order_id = body.get("razorpay_order_id")
        razorpay_payment_id = body.get("razorpay_payment_id")
        razorpay_signature = body.get("razorpay_signature")
        amount = Decimal(str(body.get("amount")))

        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }

        razorpay_client.utility.verify_payment_signature(params_dict)

        wallet, _ = Wallet.objects.get_or_create(user=user)
        wallet.credit(amount)

        WalletTransaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type="CREDIT",
            razorpay_payment_id=razorpay_payment_id,
        )

        return JsonResponse(
            {"success": True, "message": "Wallet credited successfully"}
        )

    except razorpay.errors.SignatureVerificationError:
        return JsonResponse(
            {"success": False, "error": "Signature verification failed"}
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import get_object_or_404

from wallet.models import Wallet, WalletTransaction
from accounts.models import Employee, Customer

import time
import json
from decimal import Decimal


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from accounts.models import CustomUser
from home.models import CustomProduct


# @csrf_exempt
# def api_save_custom_product(request):
#     if request.method != "POST":
#         return JsonResponse({"success": False, "error": "POST required"})

#     try:
#         data = json.loads(request.body)

#         user_id = data.get("user_id")  # Flutter must send this
#         user = CustomUser.objects.get(id=user_id)

#         CustomProduct.objects.create(
#             user=user,
#             name=data.get("product_name"),
#             size=data.get("size"),
#             material=data.get("material"),
#             other_material=data.get("other_material"),
#             message=data.get("message"),
#         )

#         return JsonResponse({"success": True})

#     except Exception as e:
#         return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
def api_save_custom_product(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required"})

    # 🚀 Authenticate
    user, error = get_user_from_token(request)
    if not user:
        return JsonResponse({"success": False, "error": error}, status=401)

    try:
        data = json.loads(request.body)

        CustomProduct.objects.create(
            user=user,
            name=data.get("product_name"),
            size=data.get("size"),
            material=data.get("material"),
            other_material=data.get("other_material"),
            message=data.get("message"),
        )

        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# API IMPORTS
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from django.db.models import Q
from home.models import Booking
from employee.models import ServiceImage
from .serializers import (
    ServiceImageSerializer,
)  # Assuming serializer is in current directory


# SESSION CHECK API
@csrf_exempt
def session_status_api(request):
    """Returns whether the current user session is active."""
    if request.user.is_authenticated:
        return JsonResponse(
            {
                "success": True,
                "is_logged_in": True,
                "user": {
                    "id": request.user.id,
                    "email": request.user.email,
                    "full_name": request.user.full_name,
                    "role": request.user.role,
                },
            }
        )
    return JsonResponse({"success": True, "is_logged_in": False})


# LOGOUT API
@csrf_exempt
def logout_api(request):
    logout(request)
    return JsonResponse({"success": True, "message": "Logged out successfully"})


# SAVE BOOKING API
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_booking_api(request):
    data = request.data
    try:
        # Required fields validation
        required = [
            "service_name",
            "contact_number",
            "email",
            "address",
            "pin_code",
            "state",
            "city",
            "total_walls",
            "width",
            "height",
            "total_sqft",
            "appointment_date",
            "total_amount",
        ]
        for field in required:
            if not data.get(field):
                return Response(
                    {"success": False, "message": f"{field} is required"}, status=400
                )

        # Date format fix
        appointment = data.get("appointment_date")
        try:
            appointment_date = datetime.strptime(appointment, "%d-%m-%Y").date()
        except:
            appointment_date = datetime.strptime(appointment, "%Y-%m-%d").date()

        next_id = Booking.objects.count() + 1
        booking_id = f"RCC{next_id}"

        design_name = data.get("selected_design_name")
        design_price = (
            float(data.get("selected_design_price"))
            if data.get("selected_design_price")
            else None
        )
        custom_design_file = request.FILES.get("custom_design")

        if design_name:
            art_type = "Selected Design"
        elif custom_design_file:
            art_type = "Custom Upload"
            design_price = design_price if design_price else 0
        else:
            art_type = "Standard Service"

        booking = Booking.objects.create(
            customer_name=request.user.full_name or request.user.email,
            customer_user_id=request.user.id,
            booking_id=booking_id,
            service_name=data.get("service_name"),
            contact_number=data.get("contact_number"),
            email=data.get("email"),
            address=data.get("address"),
            pin_code=data.get("pin_code"),
            state=data.get("state"),
            city=data.get("city"),
            total_walls=data.get("total_walls"),
            width=data.get("width"),
            height=data.get("height"),
            total_sqft=data.get("total_sqft"),
            appointment_date=appointment_date,
            design_names=design_name,
            type_of_art_booked=art_type,
            price_of_design=design_price,
            customer_design=custom_design_file,
            total_amount=data.get("total_amount"),
        )

        # Email trigger (optional)
        try:
            send_mail(
                f"Booking Confirmation - {booking.booking_id}",
                f"Dear {booking.customer_name}, your booking {booking.booking_id} is confirmed.",
                settings.DEFAULT_FROM_EMAIL,
                [booking.email],
            )
        except Exception as e:
            print("Email Error", e)

        return Response(
            {
                "success": True,
                "message": "Booking saved successfully",
                "booking": {
                    "id": booking.id,
                    "booking_id": booking.booking_id,
                    "total_amount": booking.total_amount,
                    "customer_name": booking.customer_name,
                },
            },
            status=200,
        )

    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=500)


# EXPLORE SERVICE API
@api_view(["GET"])
@permission_classes([AllowAny])
def explore_service_api(request, service_type):
    service_dict = {
        "3d-wall-art": "3D Wall Art",
        "3d-floor-art": "3D Floor Art",
        "mural-art": "Mural Art",
        "mural": "Mural Art",
        "metro-advertisement": "Metro Advertisement",
        "outdoor-advertisement": "Outdoor Advertisement",
        "school-painting": "School Painting",
        "selfie-painting": "Selfie Painting",
        "madhubani-painting": "Madhubani Painting",
        "texture-painting": "Texture Painting",
        "stone-murti": "Stone Murti",
        "Zenith-Collection": "Zenith Collection",
        "scrap-animal-art": "Scrap Animal Art",
        "nature-fountain": "Nature & Water Fountain",
        "fountain-art": "Nature & Water Fountain",
        "cartoon-painting": "Cartoon Art",
        "home-painting": "Home Painting",
    }
    service_name = service_dict.get(service_type, "Service")
    query_term = service_name

    # special cases
    if service_name == "Mural Art":
        query_term = "Mural"
    elif service_name == "Nature & Water Fountain":
        query_term = "Fountain"

    # Filtering logic
    if request.user.is_authenticated and request.user.is_staff:
        db_images = ServiceImage.objects.filter(
            type_of_art__icontains=query_term, is_approved=True
        )
    elif request.user.is_authenticated:
        db_images = ServiceImage.objects.filter(
            type_of_art__icontains=query_term
        ).filter(
            Q(is_verified_pic=True) | Q(userupload_id=request.user.id), is_approved=True
        )
    else:
        db_images = ServiceImage.objects.filter(
            type_of_art__icontains=query_term, is_verified_pic=True, is_approved=True
        )

    serializer = ServiceImageSerializer(db_images, many=True)

    return Response(
        {
            "service_name": service_name,
            "service_slug": service_type,
            "images": serializer.data,
        }
    )


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from employee.models import ServiceImage
import json

User = get_user_model()

# @csrf_exempt
# def api_service_image_upload(request):
#     if request.method != "POST":
#         return JsonResponse({"success": False, "error": "POST required"})

#     try:
#         name = request.POST.get("image_name")
#         price = request.POST.get("price")
#         width = request.POST.get("width")
#         height = request.POST.get("height")
#         min_size = f"{width} * {height}"
#         type_of_art = request.POST.get("type_of_art")
#         image = request.FILES.get("image")

#         user_id = request.POST.get("user_id")
#         user_name = "Anonymous"

#         if user_id:
#             try:
#                 user = User.objects.get(id=user_id)
#                 user_name = user.full_name if hasattr(user, "full_name") else user.email
#             except:
#                 user_name = "Anonymous"

#         ServiceImage.objects.create(
#             image_name=name,
#             price=price,
#             min_size=min_size,
#             type_of_art=type_of_art,
#             image=image,
#             userupload_id=user_id,
#             userupload_name=user_name
#         )

#         return JsonResponse({
#             "success": True,
#             "message": "Service image uploaded successfully!"
#         })

#     except Exception as e:
#         return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
def api_service_image_upload(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required"})

    # 🚀 Get user from token
    user, error = get_user_from_token(request)
    if not user:
        return JsonResponse({"success": False, "error": error}, status=401)

    try:
        name = request.POST.get("image_name")
        price = request.POST.get("price")
        width = request.POST.get("width")
        height = request.POST.get("height")
        min_size = f"{width} * {height}"
        type_of_art = request.POST.get("type_of_art")
        image = request.FILES.get("image")

        ServiceImage.objects.create(
            image_name=name,
            price=price,
            min_size=min_size,
            type_of_art=type_of_art,
            image=image,
            userupload_id=user.id,
            userupload_name=user.full_name or user.email,
        )

        return JsonResponse({"success": True, "message": "Image uploaded successfully"})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from accounts.models import Employee
from .serializers import EmployeeSerializer


# ✅ API 1: Get ALL artists (No filters)
@api_view(["GET"])
def api_get_all_artists(request):
    artists = Employee.objects.all().order_by("-id")
    serializer = EmployeeSerializer(artists, many=True)
    return Response({"success": True, "artists": serializer.data})


# ✅ API 2: Get FILTERED artists
@api_view(["GET"])
def api_get_filtered_artists(request):
    query = Employee.objects.all()

    # Get filters
    artist_id = request.GET.get("artist_id")
    name = request.GET.get("name")
    pin_code = request.GET.get("pin_code")
    address = request.GET.get("address")
    work_type = request.GET.get("work_type")
    experience_years = request.GET.get("experience_years")

    # Artist ID — supports ras5, RAS10, 7, etc.
    if artist_id:
        clean_id = artist_id.upper().replace("RAS", "").strip()
        if clean_id.isdigit():
            query = query.filter(id=clean_id)

    if name:
        query = query.filter(full_name__icontains=name)
    if pin_code:
        query = query.filter(pincode__icontains=pin_code)
    if address:
        query = query.filter(
            Q(village__icontains=address)
            | Q(city__icontains=address)
            | Q(state__icontains=address)
        )
    if work_type:
        query = query.filter(type_of_work__icontains=work_type)
    if experience_years:
        try:
            exp = int(experience_years)
            query = query.filter(experience__gte=exp)
        except:
            pass

    serializer = EmployeeSerializer(query, many=True)
    return Response({"success": True, "artists": serializer.data})


# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
# from django.utils import timezone
# from accounts.models import Customer
# from home.models import Review

# @csrf_exempt
# @login_required
# def api_create_review(request):
#     """Create new customer review"""
#     if request.method != "POST":
#         return JsonResponse({"success": False, "error": "POST method required"}, status=405)

#     try:
#         # Ensure logged-in user is a customer
#         try:
#             customer = Customer.objects.get(user=request.user)
#         except Customer.DoesNotExist:
#             return JsonResponse({"success": False, "error": "Only customers can submit reviews"}, status=403)

#         name = request.POST.get("name")
#         email = request.POST.get("email")
#         review_text = request.POST.get("customer_review")
#         rating = request.POST.get("rating")
#         review_image = request.FILES.get("image")

#         if not (name and email and rating):
#             return JsonResponse({"success": False, "error": "Missing required fields"}, status=400)

#         review = Review.objects.create(
#             customer_id=str(customer.id),
#             customer_name=name,
#             customer_email=email,
#             customer_review=review_text or "",
#             rating=int(rating),
#             review_image=review_image,
#             review_date=timezone.now(),
#         )

#         profile_pic_url = customer.customer_photo.url if customer.customer_photo else None

#         return JsonResponse({
#             "success": True,
#             "message": "Review submitted successfully!",
#             "data": {
#                 "id": review.id,
#                 "customer_id": review.customer_id,
#                 "name": review.customer_name,
#                 "email": review.customer_email,
#                 "customer_review": review.customer_review,
#                 "rating": review.rating,
#                 "image": review.review_image.url if review.review_image else None,
#                 "profile_pic": profile_pic_url,
#                 "created_at": review.review_date.strftime("%Y-%m-%d %H:%M"),
#             }
#         })

#     except ValueError:
#         return JsonResponse({"success": False, "error": "Invalid rating value"}, status=400)
#     except Exception as e:
#         return JsonResponse({"success": False, "error": str(e)}, status=500)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.models import Customer
from home.models import Review
from django.utils import timezone
from .views import get_user_from_token  # Make sure the import path is correct


@csrf_exempt
def api_create_review(request):
    """Create new customer review"""
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "POST method required"}, status=405
        )

    # 🚀 Authenticate user from token
    user, error = get_user_from_token(request)
    if not user:
        return JsonResponse({"success": False, "error": error}, status=401)

    try:
        # Ensure logged-in user is a customer
        try:
            customer = Customer.objects.get(user=user)
        except Customer.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Only customers can submit reviews"},
                status=403,
            )

        name = request.POST.get("name")
        email = request.POST.get("email")
        review_text = request.POST.get("customer_review")
        rating = request.POST.get("rating")
        review_image = request.FILES.get("image")

        if not (name and email and rating):
            return JsonResponse(
                {"success": False, "error": "Missing required fields"}, status=400
            )

        review = Review.objects.create(
            customer_id=str(customer.id),
            customer_name=name,
            customer_email=email,
            customer_review=review_text or "",
            rating=int(rating),
            review_image=review_image,
            review_date=timezone.now(),
        )

        profile_pic_url = (
            customer.customer_photo.url if customer.customer_photo else None
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Review submitted successfully!",
                "data": {
                    "id": review.id,
                    "customer_id": review.customer_id,
                    "name": review.customer_name,
                    "email": review.customer_email,
                    "customer_review": review.customer_review,
                    "rating": review.rating,
                    "image": review.review_image.url if review.review_image else None,
                    "profile_pic": profile_pic_url,
                    "created_at": review.review_date.strftime("%Y-%m-%d %H:%M"),
                },
            }
        )

    except ValueError:
        return JsonResponse(
            {"success": False, "error": "Invalid rating value"}, status=400
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def api_get_reviews(request):
    """Return reviews list for Flutter"""
    reviews = Review.objects.all().order_by("-review_date")

    data = []
    for r in reviews:
        data.append(
            {
                "id": r.id,
                "customer_id": r.customer_id,
                "name": r.customer_name,
                "email": r.customer_email,
                "customer_review": r.customer_review,
                "rating": r.rating,
                "image": r.review_image.url if r.review_image else None,
                "created_at": r.review_date.strftime("%Y-%m-%d %H:%M"),
            }
        )

    return JsonResponse({"success": True, "reviews": data})


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from home.models import Booking
from .serializers import BookingSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_orders_api(request):
    # Only allow customer role
    if request.user.role != "customer":
        return Response({"success": False, "message": "Not allowed"}, status=403)

    # Get all bookings for customer
    bookings = Booking.objects.filter(customer_user_id=request.user.id).order_by(
        "-created_at"
    )

    serializer = BookingSerializer(bookings, many=True)

    return Response(
        {"success": True, "count": bookings.count(), "data": serializer.data}
    )


# api/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from home.models import Booking
from .serializers import BookingSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def employee_bookings_api(request):
    # Only employees are allowed
    if request.user.role != "employee":
        return Response({"success": False, "message": "Not allowed"}, status=403)

    bookings = Booking.objects.filter(assigned_employee=request.user).order_by(
        "-created_at"
    )

    serializer = BookingSerializer(bookings, many=True)

    return Response(
        {"success": True, "count": bookings.count(), "data": serializer.data}
    )


# api/views.py

from decimal import Decimal
from django.shortcuts import get_object_or_404
from wallet.models import Wallet, WalletTransaction


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def booking_assignment_action_api(request, booking_id, action):
    # Only employees
    if request.user.role != "employee":
        return Response({"success": False, "message": "Not allowed"}, status=403)

    booking = get_object_or_404(Booking, id=booking_id)
    employee = request.user

    # Security check
    if booking.assigned_employee != employee or booking.assignment_status != "assigned":
        return Response(
            {"success": False, "message": "Invalid action or unauthorized access"},
            status=400,
        )

    # Accept booking
    if action == "accept":
        wallet = Wallet.objects.filter(user=employee).first()

        if wallet and wallet.balance >= Decimal("60.00"):
            wallet.balance -= Decimal("60.00")
            wallet.save()

            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type="DEBIT",
                amount=Decimal("60.00"),
                razorpay_payment_id=None,
            )

            booking.assignment_status = "accepted"
            booking.save()

            return Response(
                {"success": True, "message": "Booking accepted. ₹60 deducted"}
            )

        else:
            return Response(
                {"success": False, "message": "Insufficient wallet balance"}, status=400
            )

    # Decline booking
    elif action == "decline":
        booking.assignment_status = "declined"
        booking.assigned_employee = None
        booking.save()

        return Response({"success": True, "message": "Booking declined"})

    return Response({"success": False, "message": "Invalid action"}, status=400)


# api/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from home.models import Booking
from accounts.models import CustomUser
from .serializers import BookingSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_bookings_api(request):
    # only admin
    if request.user.role != "admin":
        return Response({"success": False, "message": "Not allowed"}, status=403)

    status_filter = request.GET.get("status")

    if status_filter and status_filter.lower() != "all":
        bookings = Booking.objects.filter(
            Q(status=status_filter) | Q(assignment_status=status_filter)
        ).order_by("-created_at")
    else:
        bookings = Booking.objects.all().order_by("-created_at")

    serializer = BookingSerializer(bookings, many=True)

    return Response(
        {"success": True, "count": bookings.count(), "data": serializer.data}
    )


from django.shortcuts import get_object_or_404


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_update_booking_status_api(request, booking_id):
    if request.user.role != "admin":
        return Response({"success": False, "message": "Not allowed"}, status=403)

    new_status = request.data.get("status")
    if not new_status:
        return Response({"success": False, "message": "status required"}, status=400)

    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = new_status
    booking.save()

    return Response({"success": True, "message": "Status updated"})


from django.core.mail import send_mail
from django.conf import settings
from accounts.models import Employee


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_assign_booking_api(request, booking_id):
    if request.user.role != "admin":
        return Response({"success": False, "message": "Not allowed"}, status=403)

    employee_id = request.data.get("employee_id")
    if not employee_id:
        return Response(
            {"success": False, "message": "employee_id required"}, status=400
        )

    booking = get_object_or_404(Booking, id=booking_id)
    employee = get_object_or_404(CustomUser, id=employee_id)

    # Assign
    booking.assigned_employee = employee
    booking.assignment_status = "assigned"
    booking.save()

    # fetch email
    employee_profile = Employee.objects.filter(user=employee).first()
    employee_email = employee_profile.email_address if employee_profile else None

    if employee_email:
        service = booking.service_name
        booking_date = booking.appointment_date
        city = booking.city
        state = booking.state

        msg = f"""
Dear {employee.full_name or employee.email},

You have received a new booking request.

🔹 Service: {service}
🔹 Date: {booking_date}
🔹 City: {city}
🔹 State: {state}

⚠️ Customer privacy protection:
- Customer phone number: ❌ Hidden
- Customer email: ❌ Hidden
- Customer full address: ❌ Hidden

Login to your dashboard to accept it.

Regards,
RColorcraft Bookings Team
"""

        try:
            send_mail(
                subject="New Booking Assigned — Action Required",
                message=msg,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[employee_email],
                fail_silently=False,
            )
        except Exception as e:
            # still return success (email failure shouldn't block)
            return Response(
                {
                    "success": True,
                    "message": "Assigned, but email sending failed",
                    "error": str(e),
                }
            )

    return Response(
        {
            "success": True,
            "message": "Booking assigned successfully",
            "assigned_to": employee.full_name,
        }
    )


from .serializers import AdminEmployeeListSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_employee_list_api(request):
    if request.user.role != "admin":
        return Response({"success": False, "message": "Not allowed"}, status=403)

    employees = CustomUser.objects.filter(role="employee", is_active=True)

    serializer = AdminEmployeeListSerializer(employees, many=True)

    return Response(
        {"success": True, "count": employees.count(), "data": serializer.data}
    )


from django.http import JsonResponse
from django.contrib.auth import login, authenticate, get_user_model

User = get_user_model()


def ajax_signup(request):
    try:
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")

            if not email or not password:
                return JsonResponse(
                    {"success": False, "error": "Email and password required"}
                )

            user = User.objects.filter(email=email).first()

            if user:
                user = authenticate(request, username=email, password=password)
                if user:
                    login(request, user)
                    return JsonResponse({"success": True})
                else:
                    return JsonResponse({"success": False, "error": "Wrong password"})

            user = User.objects.create_user(
                username=email, email=email, password=password
            )

            login(request, user)

            return JsonResponse({"success": True})

        return JsonResponse({"success": False})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
