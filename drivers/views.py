from users.models import Account, User, Notification
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserForm, DriverProfileForm, RideBookingForm
from .models import Driver, Ride
# from django.contrib.gis.db.models.functions import Distance
# from django.contrib.gis.geos import Point
from django.contrib.auth import login, authenticate, logout
import datetime
from users.middlewares.auth import driver_check_middleware
from django.conf import settings


def register_driver(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = DriverProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = User.objects.create_user(
                username=user_form.cleaned_data['username'],
                email=user_form.cleaned_data['email'],
                password=user_form.cleaned_data['password1'],
                status="Driver"
            )
            driver_info = Driver.objects.create(
                user=user,
                license_number=profile_form.cleaned_data["license_number"],
                color=profile_form.cleaned_data["color"],
                phone_number=profile_form.cleaned_data['phone_number'],
                car_model=profile_form.cleaned_data['car_model'],
                latitude=profile_form.cleaned_data["latitude"],
                longitude=profile_form.cleaned_data["longitude"],
                is_available=False,
            )
            driver_info.save()
            # Authenticate the user
            user = authenticate(username=user_form.cleaned_data['username'],
                                password=user_form.cleaned_data['password1'])
            if user is not None:
                login(request, user)
                Notification.objects.create(
                    user=user,
                    notification_type=3,
                    has_seen=False
                )
                return redirect('driver_dashboard')  # Redirect to success page
    else:
        # form = CombinedRegistrationForm()
        user_form = UserForm()
        profile_form = DriverProfileForm()
        context = {
            "user_form": user_form,
            "profile_form": profile_form
        }
    return render(request, "drivers/register_driver.html", context)


@login_required
def update_driver_profile(request):
    user = request.user
    driver_profile = request.user.driver

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = DriverProfileForm(request.POST, instance=driver_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('driver_dashboard')  # redirect to a profile detail page


@login_required
@driver_check_middleware
def driver_dashboard(request):
    notifications = Notification.objects.filter(user=request.user, has_seen=False)
    current_rides = Ride.objects.filter(driver=request.user.driver, status='accepted')
    available_rides = Ride.objects.filter(driver=request.user.driver, status='pending').order_by("-id")[:5]
    ride_history = Ride.objects.filter(driver=request.user.driver).exclude(status='pending')
    user_form = UserForm(instance=request.user)
    profile_form = DriverProfileForm(instance=request.user.driver)

    context = {
        "notifications": notifications,
        "now": datetime.datetime.now().hour,
        'driver_profile': request.user,
        'current_rides': current_rides,
        'available_rides': available_rides,
        'ride_history': ride_history,
        "user_form": user_form,
        "profile_form": profile_form,

    }
    return render(request, "drivers/driver_dashboard.html", context)


@login_required
def available_drivers(request):
    notifications = Notification.objects.filter(user=request.user, has_seen=False)
    drivers = Driver.objects.filter(is_available=True)

    context = {
        "notifications": notifications,
        "drivers": drivers
    }
    return render(request, 'drivers/available_drivers.html', context)


def available_drivers_json(request):
    drivers = Driver.objects.filter(is_available=True)

    # filtered_drivers = []
    # for driver in Driver.objects.all():
    #     driver_location = (driver.location.latitude, driver.location.longitude)
    #     distance_in_meters = geopy.distance.distance(user_location, driver_location).m
    #
    #     # Filter based on desired radius (e.g., 10 kilometers)
    #     if distance_in_meters <= 10000:  # 10 km = 10000 meters
    #         filtered_drivers.append(driver)

    drivers_data = [
        {
            "username": driver.user.username,
            "phone_number": driver.phone_number,
            "car_model": driver.car_model,
            "latitude": driver.latitude,
            "longitude": driver.longitude
        } for driver in drivers
    ]
    return JsonResponse(drivers_data, safe=False)


@login_required
def delete_account(request):
    user = request.user
    user.delete()
    logout(request)
    return redirect('login')

# def service_worker(request):
#     with open(settings.PWA_SERVICE_WORKER_PATH) as serviceworker_file:
#         response = HttpResponse(
#             serviceworker_file.read(),
#             content_type="application/javascript",
#         )
#     return response
#
#
# def manifest(request):
#     return render(
#         request,
#         "manifest.json",
#         {
#             setting_name: getattr(settings, setting_name)
#             for setting_name in dir(settings)
#             if setting_name.startswith("PWA_")
#         },
#         content_type="application/json",
#     )
#
#
# def offline(request):
#     return render(request, "drivers/offline.html")