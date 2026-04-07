from django.shortcuts import redirect
from django.urls import resolve, Resolver404
from .models import Employee


class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.profile_incomplete = False  # default

        allowed_urls = [
            "/edit_profile/",
            "/wallet/",
            "/accounts/logout/",
            "/accounts/login/",
            "/accounts/save_employee_signup/",
            "/accounts/verify_employee_otp/",
            "/accounts/save_customer_signup/",
            "/accounts/verify_customer_otp/",
            "/logout/",
            "/login/",
            "/media/",
            "/static/",
            "/admin/",
        ]

        allowed_url_names = [
            "logout",
            "login",
            "edit_profile",
            "wallet",
        ]

        if (
            request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role == "employee"
        ):
            current_path = request.path

            is_allowed = any(current_path.startswith(url) for url in allowed_urls)

            if not is_allowed:
                try:
                    resolved = resolve(current_path)
                    if resolved.url_name in allowed_url_names:
                        is_allowed = True
                except Resolver404:
                    pass

            try:
                employee = Employee.objects.get(user=request.user)

                if (
                    not employee.fathers_name
                    or not employee.dob
                    or not employee.aadhar_card_no
                    or not employee.passport_photo
                ):
                    request.profile_incomplete = True

            except Employee.DoesNotExist:
                pass

        response = self.get_response(request)
        return response
