from django.contrib import admin
from .models import User, Notification, Account
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "date_joined"]
    list_per_page = 10
    list_filter = ["username"]
    search_fields = ["username", "department", "email", "first_name"]


class AccountAdmin(admin.ModelAdmin):
    list_display = ["user", "amount", "date_added"]
    list_per_page = 10
    list_filter = ["user"]
    search_fields = ["user__username"]


class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "notification_type", "date_posted", "has_seen"]
    list_per_page = 10
    search_fields = ["user__username"]


admin.site.register(User, UserAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Notification, NotificationAdmin)
