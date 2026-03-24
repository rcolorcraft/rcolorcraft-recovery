from django.urls import path
from .views import (
    api_save_custom_product,
    save_customer_signup_api,
    verify_customer_otp_api,
    save_employee_signup_api,
    verify_employee_otp_api,
    login_api,
    api_create_order,
    api_verify_payment,
)
from .views import (
    api_get_customer_profile,
    api_update_customer_profile,
    save_booking_api,
    explore_service_api,
    session_status_api,
    logout_api,
)
from .views import (
    api_get_employee_profile,
    api_update_employee_profile,
    api_service_image_upload,
)
from .views import (
    api_get_employee_profile,
    api_update_employee_profile,
    api_get_all_artists,
    api_get_filtered_artists,
    api_create_review,
    api_get_reviews,
    my_orders_api,
)
from .views import employee_bookings_api, booking_assignment_action_api
from .views import (
    admin_bookings_api,
    admin_update_booking_status_api,
    admin_assign_booking_api,
)
from .views import admin_employee_list_api

from . import views

app_name = "api"

urlpatterns = [
    path("ajax-signup/", views.ajax_signup, name="ajax-signup"),
    path("signup_api/", save_customer_signup_api, name="customer_signup"),
    path("verify_otp/", verify_customer_otp_api, name="verify_customer_otp"),
    path("signup_api_emp/", save_employee_signup_api, name="employee_signup"),
    path("verify_otp_emp/", verify_employee_otp_api, name="verify_employee_otp"),
    path("login_api/", login_api, name="login_api"),
    path("wallet/create-order/", api_create_order, name="api_create_order"),
    path("wallet/verify-payment/", api_verify_payment, name="api_verify_payment"),
    path("customer/profile/", api_get_customer_profile),
    path("customer/profile/update/", api_update_customer_profile),
    path("employee/profile/", api_get_employee_profile),
    path("employee/profile/update/", api_update_employee_profile),
    path("custom-product/save/", api_save_custom_product),
    path("save-booking/", save_booking_api, name="save_booking_api"),
    path(
        "explore/<str:service_type>/", explore_service_api, name="explore_service_api"
    ),
    path("session-status/", session_status_api, name="session_status_api"),
    path("logout_api/", logout_api, name="logout_api"),
    path("service-image/upload/", api_service_image_upload),
    path("artists/", api_get_all_artists),
    path("artists/filter/", api_get_filtered_artists),
    path("create-review/", api_create_review, name="api_create_review"),
    path("reviews/", api_get_reviews, name="api_get_reviews"),
    path("my-orders/", my_orders_api, name="my_orders_api"),
    path("employee/bookings/", employee_bookings_api, name="employee_bookings_api"),
    path(
        "employee/booking/<int:booking_id>/<str:action>/",
        booking_assignment_action_api,
        name="booking_assignment_action_api",
    ),
    path("admin/bookings/", admin_bookings_api, name="admin_bookings_api"),
    path(
        "admin/booking/<int:booking_id>/status/",
        admin_update_booking_status_api,
        name="admin_update_booking_status_api",
    ),
    path(
        "admin/booking/<int:booking_id>/assign/",
        admin_assign_booking_api,
        name="admin_assign_booking_api",
    ),
    path("admin/employees/", admin_employee_list_api, name="admin_employee_list_api"),
]
