from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import translation
from django.shortcuts import render


import logging

logger = logging.getLogger(__name__)


# def home(request):
#     return render(request, "home/home.html")


def home_view(request):
    current_lang = translation.get_language()
    print(f"\n{'='*60}")
    print(f"🏠 HOME VIEW DEBUG")
    print(f"{'='*60}")
    print(f"Current Language: {current_lang}")
    print(f"Session Language: {request.session.get('django_language', 'Not Set')}")
    print(f"Request Path: {request.path}")
    print(f"Accept-Language Header: {request.META.get('HTTP_ACCEPT_LANGUAGE', 'None')}")
    logger.info(f"Home view accessed with language: {current_lang}")
    print(f"{'='*60}\n")
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def contact_us(request):
    return render(request, "contact_us.html")


def explore(request):
    return render(request, "exlore.html")


from django.shortcuts import render


def edit_profile(request):
    return render(request, "edit_profile.html")


def book_service(request, service_name):
    # service_name will be "3d-art", "mural", or "normal-paint"
    return render(request, "book_service.html", {"service_name": service_name})


from django.shortcuts import render
from employee.models import ServiceImage  # Make sure to import your model

# ... (imports)
from django.db.models import Q


# views.py
def explore_service(request, service_type):
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
        "pillere-painting": "Pillere Painting",
        "stone-murti": "Stone Murti",
        "statue-art": "Statue Art",
        "scrap-animal-art": "Scrap Animal Art",
        "nature-fountain": "Nature & Water Fountain",
        "fountain-art": "Nature & Water Fountain",
        "cartoon-painting": "Cartoon Painting",
        "home-painting": "Home Painting",
    }

    service_name = service_dict.get(service_type, "Service")
    query_term = service_name

    if service_name == "Mural Art":
        query_term = "Mural"
    elif service_name == "Nature & Water Fountain":
        query_term = "Fountain"

    # ✅ Updated logic
    if request.user.is_authenticated and request.user.is_staff:
        # Admins see everything
        db_images = ServiceImage.objects.filter(
            type_of_art__icontains=query_term, is_approved=True
        )
    elif request.user.is_authenticated:
        # Employees see their own + verified ones
        db_images = ServiceImage.objects.filter(
            type_of_art__icontains=query_term
        ).filter(
            Q(is_verified_pic=True) | Q(userupload_id=request.user.id), is_approved=True
        )
    else:
        # Guests see only verified ones
        db_images = ServiceImage.objects.filter(
            type_of_art__icontains=query_term, is_verified_pic=True, is_approved=True
        )
    return render(
        request,
        "explore_service.html",
        {
            "service_name": service_name,
            "db_images": db_images,
            "service_slug": service_type,
        },
    )


@csrf_exempt
def approve_service_image(request):
    if request.method == "POST":

        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({"success": False, "message": "Permission denied."})

        try:
            data = json.loads(request.body)
            image_id = data.get("id")
            image = ServiceImage.objects.get(id=image_id)
            image.is_verified_pic = True
            image.save()
            return JsonResponse(
                {"success": True, "message": "Image approved successfully!"}
            )
        except ServiceImage.DoesNotExist:
            return JsonResponse({"success": False, "message": "Image not found."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request."})


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from employee.models import ServiceImage


@csrf_exempt
def delete_service_image(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            image_id = data.get("id")
            image = ServiceImage.objects.get(id=image_id)

            user = request.user

            # Admin can delete any image
            if user.is_staff or image.userupload_id == user.id:
                image.delete()
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "message": "Permission denied."})

        except ServiceImage.DoesNotExist:
            return JsonResponse({"success": False, "message": "Image not found."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request."})


# ... (imports)
def book_service(request, service_type):
    """
    service_type: could be any of the defined service keys.
    """
    # Use the comprehensive, consistent slug map
    service_dict = {
        "3d-wall-art": "3D Wall Art ",
        "3d-floor-art": "3D Floor Art",
        "mural-art": "Mural Art",
        "mural": "Mural Art",
        "statue-painting": "Statue Art",
        "metro-advertisement": "Metro Advertisement",
        "outdoor-advertisement": "Outdoor Advertisement",
        "school-painting": "School Art",
        "selfie-painting": "Selfie Art",
        "madhubani-painting": "Madhubani Art",
        "texture-painting": "Texture Art",
        "statue": "Statue",
        "scrap-animal-art": "Scrap Animal Art",
        "nature-fountain": "Nature & Water Fountain",
        "fountain-art": "Nature & Water Fountain",
        "cartoon-painting": "Cartoon Art",
        "home-painting": "Home Art",
        # Mapping for any previous, short slugs (optional, but good for backward compatibility)
        "3d-art": "3D Wall Art",
        "advertisement-art": "Metro Advertisement",  # Guessing based on common short form
        "aesthetic-art": "Outdoor Advertisement",  # Guessing based on common short form
        "madhubani-art": "Madhubani Art",  # Guessing based on common short form
        "cartoon-art": "Cartoon Art",  # Guessing based on common short form
        "nature-art": "Nature & Water Fountain",  # Guessing based on common short form
        "scrap-yard-art": "Scrap Animal Art",  # Guessing based on common short form
        "spray-art": "Statue",  # Guessing based on context
        "structure-art": "Scrap Animal Art",  # Guessing based on context
    }

    service_name = service_dict.get(service_type, "Service")

    # Use robust filtering logic similar to explore_service
    query_term = service_name

    if service_name == "Mural Art":
        query_term = "Mural"
    elif service_name == "Nature & Water Fountain":
        query_term = "Fountain"

    # Filter images based on the specific query term using icontains
    # This replaces the entire 'if/elif/else' block for filtering
    db_images = ServiceImage.objects.filter(
        type_of_art__icontains=query_term, is_approved=True
    )

    if request.method == "POST":
        # Handle booking form submission if needed
        pass

    return render(
        request,
        "book_service.html",
        {"service_name": service_name, "db_images": db_images},
    )


def home(request):
    return render(request, "home.html")


from django.shortcuts import render


from django.shortcuts import render, redirect
from .models import Review


def reviews_page(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        review = request.POST.get("review")
        rating = request.POST.get("rating")
        image = request.FILES.get("image")

        Review.objects.create(
            customer_name=name,
            customer_email=email,
            customer_review=review,
            rating=rating,
            review_image=image,
        )

        return redirect("reviews_page")

    reviews = Review.objects.all().order_by("-review_date")

    return render(request, "reviews.html", {"reviews": reviews})


from django.contrib.auth import logout

# from django.shortcuts import render, redirect


def logout_view(request):
    logout(request)
    return render(request, "accounts/login.html")


from django.shortcuts import render
from django.db.models import Q
from accounts.models import Employee


def artists(request):
    query = Employee.objects.all()

    # Get filters
    artist_id = request.GET.get("artist_id")
    name = request.GET.get("name")
    pin_code = request.GET.get("pin_code")
    address = request.GET.get("address")
    work_type = request.GET.get("work_type")
    experience_years = request.GET.get("experience_years")

    # Filter by Artist ID (supports RAS5, ras12, 8 etc.)
    if artist_id:
        clean_id = (
            artist_id.upper().replace("RAS", "").strip()
        )  # ensures case-insensitive
        if clean_id.isdigit():
            query = query.filter(id=clean_id)

    # Apply filters with Q objects
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
            experience_years = int(experience_years)
            query = query.filter(experience__gte=experience_years)
        except ValueError:
            pass  # ignore invalid input

    return render(request, "artist.html", {"artists": query})


from .models import Review
import uuid

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Review


@csrf_exempt
@require_POST
def save_review(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse(
                {"success": False, "error": "User not authenticated"}, status=401
            )

        # Ensure logged-in user is a customer
        try:
            customer = Customer.objects.get(user=request.user)
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

        # ✅ Convert customer.id to string since customer_id is CharField
        review = Review.objects.create(
            customer_id=str(customer.id),  # Convert to string
            customer_name=name,
            customer_email=email,
            customer_review=review_text or "",
            rating=int(rating),  # Ensure integer
            review_image=review_image,
        )

        # Force save and verify
        review.save()

        # Debug print
        print(f"✅ Review saved successfully: {review.id} - {review.customer_name}")
        profile_pic_url = (
            customer.customer_photo.url if customer.customer_photo else None
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Review submitted successfully!",
                "data": {
                    "customer_id": review.customer_id,
                    "name": review.customer_name,
                    "email": review.customer_email,
                    "customer_review": review.customer_review,
                    "rating": review.rating,
                    "profile_pic": profile_pic_url,
                    "image": review.review_image.url if review.review_image else None,
                    "created_at": review.review_date.strftime("%Y-%m-%d %H:%M"),
                },
            }
        )

    except ValueError as e:
        print(f"❌ ValueError: {e}")
        return JsonResponse(
            {"success": False, "error": f"Invalid rating value: {str(e)}"}, status=400
        )
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback

        traceback.print_exc()
        return JsonResponse({"success": False, "error": str(e)}, status=500)


from .models import Booking

# def bookings(request):
#     status_filter = request.GET.get('status')  # ?status=pending, ?status=all
#     if status_filter and status_filter.lower() != "all":
#         bookings = Booking.objects.filter(status=status_filter)
#     else:
#         bookings = Booking.objects.all()

#     return render(request, 'bookings.html', {'bookings': bookings})
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Booking
from accounts.models import CustomUser  # Assuming CustomUser is in accounts app
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q


# def update_booking_status(request, booking_id):
#     if request.method == "POST":
#         new_status = request.POST.get("status")
#         booking = get_object_or_404(Booking, id=booking_id)
#         booking.status = new_status
#         booking.save()
#     return redirect(reverse("bookings"))

from django.http import JsonResponse
from .models import Booking
from accounts.models import Customer
from datetime import datetime
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# @login_required
# @csrf_exempt
# def save_booking(request):
#     if request.method == 'POST':
#         try:
#             print("Logged-in user:", request.user, request.user.id)

#             # Get the Customer record
#             customer_qs = request.user.customers.all()
#             if not customer_qs.exists():
#                 return JsonResponse({'success': False, 'message': 'This option is only available for customers.'})

#             customer = customer_qs.first()  # the single Customer object

#             booking_id = str(uuid.uuid4())[:8]

#             appointment_date = None
#             appointment_date_str = request.POST.get('appointment_date')
#             if appointment_date_str:
#                 appointment_date = datetime.strptime(appointment_date_str, "%d-%m-%Y").date()

#             booking = Booking.objects.create(
#                 booking_id=booking_id,
#                 customer_name=customer.customer_full_name,
#                 customer_user_id=customer.id,
#                 service_name=request.POST.get('service_name'),
#                 contact_number=request.POST.get('contact_number'),
#                 email=request.POST.get('email'),
#                 address=request.POST.get('address'),
#                 pin_code=request.POST.get('pin_code'),
#                 state=request.POST.get('state'),
#                 city=request.POST.get('city'),
#                 total_walls=int(request.POST.get('total_walls', 0)),
#                 width=float(request.POST.get('width', 0)),
#                 height=float(request.POST.get('height', 0)),
#                 total_sqft=float(request.POST.get('total_sqft', 0)),
#                 appointment_date=appointment_date,
#                 payment_option="pending",
#                 payment_amount=0.00,
#                 is_paid=False
#             )

#             return JsonResponse({'success': True, 'message': 'Booking saved successfully!'})

#         except Exception as e:
#             return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import Customer, Employee  # assuming you have Employee model
from decimal import Decimal
import time
from decimal import Decimal
from wallet.models import Wallet, WalletTransaction
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required
def edit_profile_view(request):
    # List of all 29 Indian states
    INDIAN_STATES = [
        "Andhra Pradesh",
        "Arunachal Pradesh",
        "Assam",
        "Bihar",
        "Chhattisgarh",
        "Goa",
        "Gujarat",
        "Haryana",
        "Himachal Pradesh",
        "Jharkhand",
        "Karnataka",
        "Kerala",
        "Madhya Pradesh",
        "Maharashtra",
        "Manipur",
        "Meghalaya",
        "Mizoram",
        "Nagaland",
        "Odisha",
        "Punjab",
        "Rajasthan",
        "Sikkim",
        "Tamil Nadu",
        "Telangana",
        "Tripura",
        "Uttar Pradesh",
        "Uttarakhand",
        "West Bengal",
        "Delhi",
    ]

    user = request.user
    if user.role == "employee":
        employee = get_object_or_404(Employee, user=user)

        if request.method == "POST":

            prev_status = employee.status
            employee.fathers_name = request.POST.get("fathers_name") or None
            employee.dob = request.POST.get("dob")
            employee.gender = request.POST.get("gender")
            employee.house_no = request.POST.get("house_no")
            employee.village = request.POST.get("village")
            employee.city = request.POST.get("city")
            employee.state = request.POST.get("state")
            employee.pincode = request.POST.get("pincode")
            employee.aadhar_card_no = request.POST.get("aadhar_card_no")
            employee.experience = request.POST.get("experience")

            # Get multiple selected locations and join them
            selected_locations = request.POST.getlist("preferred_location")
            print("LOCATIONS:", selected_locations)
            employee.preferred_work_location = ", ".join(selected_locations)

            employee.bank_account_holder_name = (
                request.POST.get("bank_account_holder_name") or None
            )

            employee.account_no = request.POST.get("account_no") or None
            employee.ifsc_code = request.POST.get("ifsc_code") or None

            # NEW: Handle the three new optional fields
            employee.full_address = request.POST.get("full_address")
            employee.working_range = request.POST.get("working_range")
            employee.belong_to_org = request.POST.get("belong_to_org") == "on"
            employee.pan_card = request.POST.get("pan_card")
            employee.gst_no = request.POST.get("gst_no")
            employee.organization_name = request.POST.get("organization_name")

            employee.role = "employee"

            # Check if ready to take orders
            is_ready = request.POST.get("ready_to_take_orders") == "on"

            # File fields
            if "passport_photo" in request.FILES:
                employee.passport_photo = request.FILES["passport_photo"]
            if "aadhar_card_image_front" in request.FILES:
                employee.aadhar_card_image_front = request.FILES[
                    "aadhar_card_image_front"
                ]
            if "aadhar_card_image_back" in request.FILES:
                employee.aadhar_card_image_back = request.FILES[
                    "aadhar_card_image_back"
                ]

            # Multi checkbox values (list)
            employee.type_of_work = request.POST.getlist("type_of_work")

            # Handle status change and wallet deduction
            if not prev_status and is_ready:
                wallet = Wallet.objects.filter(user=user).first()

                if wallet and wallet.balance >= Decimal("20.00"):
                    wallet.balance -= Decimal("20.00")
                    wallet.save()

                    WalletTransaction.objects.create(
                        wallet=wallet,
                        transaction_type="DEBIT",
                        amount=Decimal("20.00"),
                        razorpay_payment_id=f"ACTIVATION_FEE_{user.id}_{int(time.time())}",
                    )

                    employee.status = True
                    employee.save()

                    print("Deducted ₹20 for activation fee")
                    return JsonResponse(
                        {
                            "success": True,
                            "message": "Profile updated successfully! ₹20 activation fee deducted from your wallet.",
                        }
                    )
                else:
                    employee.status = False
                    employee.save()
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "Insufficient wallet balance. Please add ₹20 to enable 'Ready to Take Orders' feature.",
                        }
                    )
            else:
                employee.full_name = request.POST.get("full_name")
                employee.status = is_ready
                employee.save()
                print("Profile saved")
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Profile updated successfully!",
                        "name": employee.full_name,
                    }
                )

        # For GET requests - prepare context
        stored_locations = employee.preferred_work_location or ""
        selected_locations = (
            [loc.strip() for loc in stored_locations.split(",")]
            if stored_locations
            else []
        )

        context = {
            "name": employee.full_name,
            "email_address": employee.email_address,
            "contact": employee.mobile,
            "passport_photo": (
                employee.passport_photo.url if employee.passport_photo else None
            ),
            "fathers_name": employee.fathers_name,
            "dob": employee.dob,
            "gender": employee.gender,
            "house_no": employee.house_no,
            "village": employee.village,
            "city": employee.city,
            "state": employee.state,
            "pincode": employee.pincode,
            "aadhar_card_no": employee.aadhar_card_no,
            "aadhar_card_image_front": (
                employee.aadhar_card_image_front.url
                if employee.aadhar_card_image_front
                else None
            ),
            "aadhar_card_image_back": (
                employee.aadhar_card_image_back.url
                if employee.aadhar_card_image_back
                else None
            ),
            "experience": employee.experience,
            "type_of_work": employee.type_of_work or [],
            "preferred_work_location": employee.preferred_work_location,
            "INDIAN_STATES": INDIAN_STATES,
            "selected_locations": selected_locations,
            "bank_account_holder_name": employee.bank_account_holder_name,
            "account_no": employee.account_no,
            "ifsc_code": employee.ifsc_code,
            # NEW: Add the three new fields to context
            "pan_card": employee.pan_card,
            "gst_no": employee.gst_no,
            "organization_name": employee.organization_name,
            "ready_to_take_orders": employee.status,
            "full_address": employee.full_address,
            "working_range": employee.working_range,
            "belong_to_org": employee.belong_to_org,
        }
        return render(request, "edit_profile.html", context)

    elif user.role == "customer":
        customer = get_object_or_404(Customer, user=user)

        if request.method == "POST":
            customer.customer_full_name = request.POST.get("name")
            customer.email = request.POST.get("email") or None
            customer.mobile = request.POST.get("contact")

            # Handle profile picture
            if "customer_photo" in request.FILES:
                customer.customer_photo = request.FILES["customer_photo"]

            customer.save()
            return JsonResponse(
                {"success": True, "message": "Profile updated successfully!"}
            )

        context = {
            "name": customer.customer_full_name,
            "email": customer.email,
            "contact": customer.mobile,
            "profile_pic": (
                customer.customer_photo.url if customer.customer_photo else None
            ),
        }
        return render(request, "edit_customers_profile.html", context)

    return render(request, "edit_profile.html", {"user": user})


def shop(request):
    # Example products
    products = [
        {
            "id": 1,
            "name": "Acrylic Paint Set",
            "price": 599,
            "image": "gallery/paint_set.jpg",
        },
        {"id": 2, "name": "Canvas Board", "price": 299, "image": "gallery/canvas.jpg"},
        {"id": 3, "name": "Brush Kit", "price": 399, "image": "gallery/brush_kit.jpg"},
        {"id": 4, "name": "Oil Pastels", "price": 199, "image": "gallery/pastels.jpg"},
    ]
    return render(request, "shop.html", {"products": products})


from django.shortcuts import render
from .models import Booking


def my_orders(request):
    if not request.user.is_authenticated or request.user.role != "customer":
        return render(request, "not_allowed.html")

    # Filter bookings based on the logged-in user's ID
    bookings = Booking.objects.filter(customer_user_id=request.user.id).order_by(
        "-created_at"
    )

    return render(request, "my_orders.html", {"bookings": bookings})


# views.py

from django.shortcuts import render
from .models import Review
from django.db.models import F
from .models import Review
from accounts.models import Customer


def home_view(request):
    reviews = Review.objects.all().order_by("-review_date")[:3]
    reviews_list = list(reviews)

    fake_reviews = [
        {
            "customer_name": "P. Reddy",
            "customer_review": "A true artist! The mural they painted for my cafe is a masterpiece.",
            "rating": 5,
            "review_image": None,
        },
        {
            "customer_name": "S. Kumar",
            "customer_review": "Excellent work and very easy to communicate with. Will definitely use their service again.",
            "rating": 5,
            "review_image": None,
        },
        {
            "customer_name": "M. Gupta",
            "customer_review": "The 3D art on my wall looks so real. It completely changed the feel of the room.",
            "rating": 5,
            "review_image": None,
        },
    ]
    # keep your same fake reviews


def home_view(request):

    reviews_list = Review.objects.all().order_by("-id")

    # Fake reviews (अगर database में कम हों)
    fake_reviews = [
        {
            "customer_name": "Rohit Sharma",
            "rating": 5,
            "review": "Amazing wall painting work!",
            "review_image": None,
        },
        {
            "customer_name": "Pawan Mehta",
            "rating": 4,
            "review": "Very creative design and good finishing.",
            "review_image": None,
        },
        {
            "customer_name": "Neha Kapoor",
            "rating": 5,
            "review": "Professional artists and beautiful artwork.",
            "review_image": None,
        },
    ]

    all_reviews = list(reviews_list)

    if len(all_reviews) < 3:
        all_reviews = all_reviews + fake_reviews

    enriched_reviews = []

    for r in all_reviews:

        # Fake reviews (dictionary)
        if isinstance(r, dict):

            rating = r["rating"]
            r["full_stars"] = range(rating)
            r["empty_stars"] = range(5 - rating)
            r["customer_photo"] = None

            enriched_reviews.append(r)

        # Database reviews (Django model)
        else:

            rating = r.rating

            setattr(r, "full_stars", range(rating))
            setattr(r, "empty_stars", range(5 - rating))

            enriched_reviews.append(r)

    context = {"reviews": enriched_reviews}

    return render(request, "home.html", context)


# views.py - Add these functions to your existing views.py

import razorpay
import time
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


@require_http_methods(["POST"])
def create_razorpay_order(request):
    try:
        # Get amount from request (convert to paise - multiply by 100)
        amount_str = request.POST.get("amount", "0")
        amount = int(float(amount_str) * 100)  # Convert to paise

        # Create unique receipt ID
        receipt_id = f"booking_{int(time.time())}"

        # Create Razorpay order
        order_data = {
            "amount": amount,
            "currency": "INR",
            "receipt": receipt_id,
            "payment_capture": 1,  # Auto capture payment
        }

        order = razorpay_client.order.create(data=order_data)

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


@csrf_exempt
@require_http_methods(["POST"])
def verify_razorpay_payment(request):
    try:
        data = json.loads(request.body)

        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")
        product_name = data.get("product_name")
        amount = data.get("amount")

        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }

        # Verify signature
        razorpay_client.utility.verify_payment_signature(params_dict)

        # 📝 Save booking/order
        from .models import BookingOrder  # or your booking model

        BookingOrder.objects.create(
            user=request.user if request.user.is_authenticated else None,
            product_name=product_name,
            amount=amount,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            status="PAID",
        )

        return JsonResponse(
            {"success": True, "message": "Payment verified successfully"}
        )

    except razorpay.errors.SignatureVerificationError:
        return JsonResponse(
            {"success": False, "error": "Payment signature verification failed"}
        )


# Add this to your views.py or update your existing save_bookings view
from django.core.mail import send_mail
from django.conf import settings

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import Booking


@csrf_exempt
@require_http_methods(["POST"])
def save_booking(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse(
                {"success": False, "message": "You must be logged in to book a service"}
            )
        print("POST DATA:", request.POST)

        # --- Standard Fields ---
        service_name = request.POST.get("service_name")
        customer_name = request.POST.get("customer_name")
        print("NAME:", customer_name)
        # 👈 YAHAN ADD KARO
        contact_number = request.POST.get("contact_number")
        email = request.POST.get("email")
        address = request.POST.get("address")
        if not contact_number or not address:
            return JsonResponse(
                {"success": False, "message": "Contact & Address required"}
            )
        pin_code = request.POST.get("pin_code")
        state = request.POST.get("state")
        city = request.POST.get("city")
        total_walls = request.POST.get("total_walls")
        width = request.POST.get("width")
        height = request.POST.get("height")
        width = float(width) if width else None
        height = float(height) if height else None
        total_sqft = request.POST.get("total_sqft") or "0"
        appointment_date = request.POST.get("appointment_date")

        # *** CRITICAL FIX: Use the calculated amount from the front-end ***
        total_amount = request.POST.get("total_amount")
        print(total_amount, "total_amount_+++++++++++++++++++++")
        # --- Design Fields (from form or null) ---
        selected_design_name = request.POST.get("selected_design_name")
        selected_design_price = request.POST.get(
            "selected_design_price"
        )  # This is the price/rate for the design
        custom_design_file = request.FILES.get(
            "custom_design"
        )  # This handles uploaded file

        required_fields = [
            service_name,
            contact_number,
            address,
            pin_code,
            state,
            city,
            total_walls,
            width,
            height,
            appointment_date,
        ]
        if not all(required_fields):
            # Check for total_sqft > 0 instead of just existence
            if not total_sqft or float(total_sqft) <= 0:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Please enter valid width/height to calculate square footage.",
                    }
                )
            return JsonResponse(
                {"success": False, "message": "Please fill all required fields"}
            )

        if appointment_date:
            try:
                # Assuming the JS sends 'DD-MM-YYYY'
                appointment_date = datetime.strptime(
                    appointment_date, "%d-%m-%Y"
                ).date()
            except ValueError:
                # Check if format is YYYY-MM-DD (standard date input fallback)
                try:
                    appointment_date = datetime.strptime(
                        appointment_date, "%Y-%m-%d"
                    ).date()
                except ValueError:
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "Invalid date format, use DD-MM-YYYY or YYYY-MM-DD",
                        }
                    )

        next_id = Booking.objects.count() + 1
        booking_id = f"RCC{next_id}"
        print("getting to it ")

        # --- Finalize Design Fields for Model ---
        design_name_to_save = selected_design_name if selected_design_name else None

        # Save the design price/rate (which was used to calculate the final amount)
        price_to_save = float(selected_design_price) if selected_design_price else None

        # Determine type_of_art_booked
        if design_name_to_save:
            art_type = "Selected Design"
        elif custom_design_file:
            art_type = "Custom Upload"
            # If custom design is uploaded, the price/rate used would be the service's default rate
            # You might want to pull the default rate here, but we'll use null/0 for simplicity.
            price_to_save = (
                price_to_save if price_to_save is not None else 0
            )  # Default price if needed
        else:
            art_type = "Standard Service"
            # If standard, the price/rate is the hardcoded base rate from your JS, which you may want to save here.
            # For now, we'll keep price_to_save as None/0 if no design selected/uploaded.
            # If you want to save the rate from SERVICE_BASE_RATES, you'd need to send it from JS or look it up here.

        booking = Booking.objects.create(
            customer_name=(
                request.user.full_name if request.user.full_name else request.user.email
            ),
            customer_user_id=request.user.id,
            booking_id=booking_id,
            service_name=service_name,
            contact_number=contact_number,
            email=email,
            address=address,
            pin_code=pin_code,
            state=state,
            city=city,
            total_walls=total_walls,
            width=width,
            height=height,
            total_sqft=total_sqft,
            appointment_date=appointment_date,
            # --- SAVING DESIGN AND PRICE ---
            design_names=design_name_to_save,
            type_of_art_booked=art_type,
            price_of_design=price_to_save,  # The per-sqft rate or design fixed price
            customer_design=custom_design_file,  # Saves the uploaded file or None
            # --- FINAL AMOUNT FIX ---
            total_amount=total_amount,
        )

        # --- SEND BOOKING CONFIRMATION EMAIL ---
        try:
            subject = f"Booking Confirmation - {booking.booking_id}"

            message = f"""
        Hello {booking.customer_name},

        Thank you for booking with RColorCraft! 🎨  
        Your booking has been successfully received.

        Here are your booking details:

        ----------------------------------------
        🆔 Booking ID: {booking.booking_id}
        🛠 Service: {booking.service_name}

        📅 Appointment Date: {appointment_date.strftime('%d-%m-%Y')}
        🏠 Address: {booking.address}, {booking.city}, {booking.state} - {booking.pin_code}

        🧱 Total Walls: {booking.total_walls}
        📐 Width x Height: {booking.width} ft x {booking.height} ft
        📏 Total Sq Ft: {booking.total_sqft}

        💰 Total Amount: ₹{booking.total_amount}

        🎨 Art Type: {booking.type_of_art_booked}
        """

            # Add design info only if applicable
            if booking.design_names:
                message += f"🖼 Selected Design: {booking.design_names}\n"
                message += f"💵 Design Rate: ₹{booking.price_of_design} per sqft\n"

            if booking.customer_design:
                message += f"📁 Custom Design Uploaded: Yes\n"

            message += "\n----------------------------------------\n"
            message += "Our team will contact you within 24 hours.\n"
            message += "Thank you for choosing RColorCraft! 😊"

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],  # customer email
                fail_silently=False,
            )

            print("BOOKING SAVED:", booking)
        except Exception as email_error:
            print("EMAIL ERROR:", email_error)

        return JsonResponse(
            {
                "success": True,
                "name": customer_name,
                "booking_id": booking.booking_id,
                "service": booking.service_name,
                "amount": booking.total_amount,
            }
        )

    except Exception as e:
        import traceback

        print(traceback.format_exc())
        return JsonResponse({"success": False, "message": str(e)})


from django.utils.decorators import method_decorator
from .models import CustomProduct


@csrf_exempt
@login_required
def save_custom_product(request):
    if request.method == "POST":
        try:
            CustomProduct.objects.create(
                user=request.user,
                name=request.POST.get("product_name"),
                size=request.POST.get("size"),
                material=request.POST.get("material"),
                other_material=request.POST.get("other_material"),
                message=request.POST.get("message"),
            )
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request"})


def is_admin(user):
    # Assuming staff/superuser status denotes an admin for booking management
    return user.is_authenticated and user.is_staff


def is_employee(user):
    # Assuming 'role' = 'employee' is set in CustomUser for workers
    return user.is_authenticated and user.role == "employee"


# --- Admin/Manager Views ---


@user_passes_test(is_admin)
def bookings(request):
    """Admin view to list all bookings and employees."""
    status_filter = request.GET.get("status")

    if status_filter and status_filter.lower() != "all":
        # Also filter by assignment_status if you want to group them
        bookings = Booking.objects.filter(
            Q(status=status_filter) | Q(assignment_status=status_filter)
        ).order_by("-created_at")
    else:
        bookings = Booking.objects.all().order_by("-created_at")

    # Fetch users who can be assigned (employees)
    employees = CustomUser.objects.filter(role="employee").order_by("full_name")

    context = {
        "bookings": bookings,
        "employees": employees,  # Passed for the assignment dropdown
    }
    return render(request, "bookings.html", context)


@user_passes_test(is_admin)
def update_booking_status(request, booking_id):
    """Admin view to change the main booking status (pending, in_process, etc.)."""
    if request.method == "POST":
        new_status = request.POST.get("status")
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = new_status
        booking.save()
    return redirect(reverse("bookings"))


# @user_passes_test(is_admin)
# def assign_booking(request, booking_id):
#     """Admin view to assign a booking to a specific employee."""
#     if request.method == "POST":
#         employee_id = request.POST.get("employee_id")
#         booking = get_object_or_404(Booking, id=booking_id)
#         employee = get_object_or_404(CustomUser, id=employee_id)

#         # Assign the employee and set status to 'assigned' (awaiting response)
#         booking.assigned_employee = employee
#         booking.assignment_status = 'assigned'
#         booking.save()

#     return redirect(reverse("bookings"))
from django.core.mail import send_mail
from django.conf import settings


@user_passes_test(is_admin)
def assign_booking(request, booking_id):
    """Admin view to assign a booking to a specific employee."""
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        booking = get_object_or_404(Booking, id=booking_id)
        employee = get_object_or_404(CustomUser, id=employee_id)

        # Assign the employee
        booking.assigned_employee = employee
        booking.assignment_status = "assigned"
        booking.save()

        # 🔍 Fetch employee profile to get email
        employee_profile = Employee.objects.filter(user=employee).first()
        employee_email = employee_profile.email_address if employee_profile else None

        # 🔥 Send assignment email
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

For more information and full details,
👉 Please login to your account and accept the order.

Regards,
RColorcraft Bookings Team
"""

            send_mail(
                subject="📢 New Booking Assigned — Action Required",
                message=msg,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[employee_email],
                fail_silently=False,
            )

    return redirect(reverse("bookings"))


# --- Employee Views ---


@user_passes_test(is_employee)
def employee_bookings(request):
    """Employee view to see all assigned bookings."""
    # Only show bookings assigned to the currently logged-in user
    bookings = Booking.objects.filter(assigned_employee=request.user).order_by(
        "-created_at"
    )

    return render(request, "employee_bookings.html", {"bookings": bookings})


@user_passes_test(is_employee)
def handle_assignment_response(request, booking_id, action):
    """Employee view to accept or decline an assignment."""
    booking = get_object_or_404(Booking, id=booking_id)
    employee = request.user  # the logged-in user

    # Security check
    if booking.assigned_employee != employee or booking.assignment_status != "assigned":
        messages.error(request, "Invalid action or unauthorized access.")
        return redirect(reverse("employee_bookings"))

    # Accept booking
    if action == "accept":
        # Deduct ₹60 from wallet
        wallet = Wallet.objects.filter(user=employee).first()

        if wallet and wallet.balance >= Decimal("60.00"):
            wallet.balance -= Decimal("60.00")
            wallet.save()

            # Log transaction
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type="DEBIT",
                amount=Decimal("60.00"),
                # description=f"Assignment fee for booking {booking.booking_id}",
                razorpay_payment_id=None,
            )

            booking.assignment_status = "accepted"
            booking.save()
            messages.success(
                request,
                f"You accepted the assignment. ₹60 has been deducted from your wallet.",
            )
        else:
            messages.error(
                request,
                "Insufficient wallet balance. You need at least ₹60 to accept this booking.",
            )
            return redirect(reverse("employee_bookings"))

    # Decline booking
    elif action == "decline":
        booking.assignment_status = "declined"
        booking.assigned_employee = None
        booking.save()
        messages.info(request, "You have declined the assignment.")

    return redirect(reverse("employee_bookings"))


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from employee.models import ServiceImage


@csrf_exempt
def update_service_price(request):
    if request.method == "POST":
        if not request.user.is_staff:
            return JsonResponse(
                {"success": False, "message": "Permission denied."}, status=403
            )
        try:
            data = json.loads(request.body)
            image_id = data.get("id")
            new_price = data.get("price")

            img = ServiceImage.objects.get(id=image_id)
            img.price = new_price
            img.save()

            return JsonResponse({"success": True})
        except ServiceImage.DoesNotExist:
            return JsonResponse({"success": False, "message": "Image not found."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request method."})


from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from accounts.models import Employee


@login_required
def toggle_block_artist(request, artist_id):
    print("CLICKED ID:", artist_id)

    artist = get_object_or_404(Employee, id=artist_id)

    print("BEFORE:", artist.block_status)

    artist.block_status = not artist.block_status
    artist.save()

    print("AFTER:", artist.block_status)

    return redirect(request.META.get("HTTP_REFERER", "/artists/"))


from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Booking


@login_required
def toggle_customer_status(request, booking_id):
    booking = get_object_or_404(
        Booking, id=booking_id, customer_user_id=request.user.id
    )

    if request.method == "POST":
        booking.customer_status = not booking.customer_status
        booking.save(update_fields=["customer_status"])

    return redirect("my_orders")


@login_required
def toggle_artist_status(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        assigned_employee=request.user,
        assignment_status="accepted",
    )

    if request.method == "POST":
        booking.artist_status = not booking.artist_status
        booking.save(update_fields=["artist_status"])

    return redirect("employee_assignments")


from django.shortcuts import render, redirect
from .models import Consultation


def home(request):
    if request.method == "POST":
        print("🔥 FORM SUBMITTED")

        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        Consultation.objects.create(
            name=name, email=email, phone=phone, message=message
        )

        return redirect("/en/?success=1")

    return render(
        request,
        "home.html",
    )


from .models import Booking


def my_assignments(request):
    bookings = Booking.objects.all()

    return render(request, "employee_bookings.html", {"bookings": bookings})


from django.shortcuts import get_object_or_404, redirect
from .models import Booking


def toggle_artist_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":
        booking.artist_status = not booking.artist_status
        booking.save()

    return redirect("my_assignments")


from django.shortcuts import render


def my_bookings(request):
    return render(request, "my_bookings.html")
