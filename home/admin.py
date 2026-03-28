from django.contrib import admin
from accounts.models import CustomUser
from .models import Consultation, Review, Customer, Artist, Assignment, Booking


admin.site.register(CustomUser)
admin.site.register(Consultation)
admin.site.register(Review)
admin.site.register(Customer)
admin.site.register(Artist)
admin.site.register(Assignment)
admin.site.register(Booking)
