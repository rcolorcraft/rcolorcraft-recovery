# accounts/middleware.py
from django.shortcuts import redirect
from django.urls import reverse, resolve, Resolver404
from .models import Employee


class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs that don't require profile completion
        allowed_urls = [
            "/edit_profile/",
            "/wallet/",
            "/accounts/logout/",
            "/accounts/login/",
            "/accounts/save_employee_signup/",
            "/accounts/verify_employee_otp/",
            "/accounts/save_customer_signup/",
            "/accounts/verify_customer_otp/",
            "/logout/",  # Added this
            "/login/",  # Added this for safety
            "/media/",
            "/static/",
            "/admin/",
        ]

        # Also allow by URL name
        allowed_url_names = [
            "logout",
            "login",
            "edit_profile",
            "wallet",
        ]

        # Check if user is authenticated and is an employee
        if (
            request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role == "employee"
        ):
            current_path = request.path

            # Check if current path is in allowed URLs
            is_allowed = any(current_path.startswith(url) for url in allowed_urls)

            # Also check by URL name
            if not is_allowed:
                try:
                    resolved = resolve(current_path)
                    if resolved.url_name in allowed_url_names:
                        is_allowed = True
                except Resolver404:
                    pass

            if not is_allowed:
                try:
                    employee = Employee.objects.get(user=request.user)

                    # Check if profile is incomplete
                    if (
                        not employee.fathers_name
                        or not employee.dob
                        or not employee.aadhar_card_no
                        or not employee.passport_photo
                    ):

                        # Redirect to edit profile
                        return redirect("/edit_profile/")

                except Employee.DoesNotExist:
                    pass

        response = self.get_response(request)
        return response
