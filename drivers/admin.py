from django.contrib import admin
from .models import *

# Register your models here.


class DriverAdmin(admin.ModelAdmin):
    list_display = ["user", "license_number", "car_model", "is_available"]
    list_filter = ["user", "license_number", "car_model", "is_available"]
    list_per_page = 10
    search_fields = ["license_number", "car_model", "user__username"]


class RideAdmin(admin.ModelAdmin):
    list_display = ["user", "driver", "start_location", "end_location", "status", "start_time"]
    list_filter = ["user", "driver", "start_location", "end_location", "status"]
    list_per_page = 10
    search_fields = ["start_location", "status", "driver__user__username", "user__username"]


admin.site.register(Driver, DriverAdmin)
admin.site.register(Ride, RideAdmin)
