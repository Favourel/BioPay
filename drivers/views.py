from users.models import Account, User, Notification
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CombinedRegistrationForm, RideBookingForm
from .models import Driver, Ride
# from django.contrib.gis.db.models.functions import Distance
# from django.contrib.gis.geos import Point
from django.contrib.auth import login, authenticate
import datetime
from users.middlewares.auth import driver_check_middleware


def register_driver(request):
    if request.method == 'POST':
        form = CombinedRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                status="Driver"
            )
            driver_info = Driver.objects.create(
                user=user,
                license_number=form.cleaned_data["license_number"],
                color=form.cleaned_data["color"],
                phone_number=form.cleaned_data['phone_number'],
                car_model=form.cleaned_data['car_model'],
                latitude=form.cleaned_data["latitude"],
                longitude=form.cleaned_data["longitude"],
                is_available=True,
            )
            driver_info.save()
            # Authenticate the user
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            if user is not None:
                login(request, user)
                Notification.objects.create(
                    user=user,
                    notification_type=3,
                    has_seen=False
                )
                return redirect('driver_dashboard')  # Redirect to success page
    else:
        form = CombinedRegistrationForm()
    return render(request, "drivers/register_driver.html", {"form": form})


@login_required
def update_driver_profile(request):
    profile = request.user.driver_profile
    if request.method == 'POST':
        form = CombinedRegistrationForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('driver_dashboard')
    else:
        form = CombinedRegistrationForm(instance=profile)
    return render(request, 'update_driver_profile.html', {'form': form})


@login_required
@driver_check_middleware
def driver_dashboard(request):
    notifications = Notification.objects.filter(user=request.user, has_seen=False)
    current_rides = Ride.objects.filter(driver=request.user.driver, status='accepted')
    available_rides = Ride.objects.filter(driver=request.user.driver, status='pending').order_by("-id")[:5]
    ride_history = Ride.objects.filter(driver=request.user.driver).exclude(status='pending')

    context = {
        "notifications": notifications,
        "now": datetime.datetime.now().hour,
        'driver_profile': request.user,
        'current_rides': current_rides,
        'available_rides': available_rides,
        'ride_history': ride_history,

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


