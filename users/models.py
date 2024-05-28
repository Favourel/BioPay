from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

username_validator = RegexValidator(
    regex=r'^[@\w.+-]{1,150}$',  # Allow letters, numbers, and specific special characters
    message='Username must consist of letters, numbers, or @/./+/-/_ characters.',
    code='invalid_username'
)
# Create your models here.


class User(AbstractUser):
    username = models.CharField(_('username'), max_length=150, unique=True, validators=[username_validator])
    phone_number = models.CharField(max_length=11, null=True, blank=True)
    picture_url = models.ImageField(default='profile_picture/download_EPBN0x6.jpg', upload_to='profile_picture')
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    department = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)


class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_added = models.DateTimeField(default=datetime.now)
    status = models.BooleanField(default=False)
    ref = models.CharField(max_length=100, null=True, unique=True)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.user}"


class Notification(models.Model):
    notification_options = [
        (1, "Funds Added"), (2, "Funds Subtracted"), (3, "Driver Account")
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
                             related_name="notification_to_user")
    notification_type = models.IntegerField(choices=notification_options)
    has_seen = models.BooleanField(default=False)
    date_posted = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.user}"
