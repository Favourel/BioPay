from decimal import Decimal
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import views as auth_view
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json

from .models import Notification, Account
from drivers.models import Ride
from users.middlewares.auth import status_check_middleware
from django.urls import reverse_lazy
from .forms import CustomAuthenticationForm
from drivers.forms import *
from geopy.distance import distance
from geopy.geocoders import Nominatim
import random
from django.shortcuts import get_object_or_404, HttpResponse, HttpResponseRedirect
from django.contrib import messages
import geopy.geocoders
from django.views.decorators.csrf import csrf_exempt
import base64
import math
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

from datetime import datetime, date, timedelta
# Create your views here.


class CustomLoginView(auth_view.LoginView):
    form_class = CustomAuthenticationForm

    def get_success_url(self):
        if self.request.user.status != "Student":
            return reverse_lazy('driver_dashboard')
        else:
            return reverse_lazy('dashboard')

@login_required
@status_check_middleware
def user_dashboard(request):
    ride_history = Ride.objects.filter(user=request.user).exclude(status="pending")
    current_rides = Ride.objects.filter(user=request.user).exclude(status='pending')
    notifications = Notification.objects.filter(user=request.user, has_seen=False)
    ride_total = sum([ride.fare for ride in Ride.objects.filter(user=request.user, status="completed")])

    month = Ride.objects.filter(user=request.user, start_time__gte=datetime.now() - timedelta(days=30)).exclude(status="pending")
    context = {
        "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY,
        "notifications": notifications,
        "now": datetime.now().hour,
        'current_rides': current_rides,
        'ride_history': ride_history,
        "ride_total": ride_total,
        "month": sum([fare.fare for fare in month])
    }
    return render(request, "users/dashboard.html", context)


@login_required
def process_topUp(request):
    data = json.loads(request.body)
    # transaction_id = datetime.datetime.now().timestamp()
    reference = str(data['ref']['reference'])

    try:
        # Get the user's account (raises DoesNotExist if not found)
        account = Account.objects.get(user=request.user)
    except Account.DoesNotExist:
        # Create a new account if it doesn't exist
        account = Account.objects.create(
            amount=Decimal(data['ref']["amount"]),
            ref=reference,
            user=request.user,
            status=True
        )
    else:
        # Update existing account balance
        account.amount += Decimal(data['ref']["amount"])
        account.save()

    notification = Notification.objects.create(
        user=request.user,
        notification_type=1
    )
    notification.save()
    return JsonResponse('Payment complete! New balance: ' + str(account.amount), safe=False)


@login_required
def search_drivers(request):
    if request.method == 'GET':
        notifications = Notification.objects.filter(user=request.user, has_seen=False)
        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')

        if not all([latitude, longitude]):
            messages.error(request, "Missing location")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        # Convert to floats
        user_latitude = float(latitude)
        user_longitude = float(longitude)

        # Create user location using Geopy
        user_location = (user_latitude, user_longitude)

        # Loop through drivers and calculate distance using Geopy
        filtered_drivers = []
        for driver in Driver.objects.filter(is_available=True):
            driver_location = (driver.latitude, driver.longitude)
            distance_in_meters = distance(user_location, driver_location).m

            # Filter based on desired radius (e.g., 10 kilometers)
            if distance_in_meters <= 10000:  # 10 km = 10000 meters
                filtered_drivers.append(driver)

        # Now you can return the filtered drivers to the frontend for display
        return render(request, 'drivers/available_drivers.html', {'drivers': filtered_drivers, "notifications": notifications})

    return HttpResponseBadRequest("Invalid request method")


@login_required
def book_ride(request):
    if request.method == 'POST':
        drop_off_location = request.POST['drop_off_location']
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        user_location = (latitude, longitude)

        geolocator = Nominatim(user_agent="drivers")
        location = geolocator.reverse(user_location)
        print(user_location)
        if location:
            start_location_string = location.address
            print(start_location_string)
        else:
            start_location_string = "Location unavailable"

        # Find the nearest available driver based on the user's location
        nearest_driver = None
        min_distance = float('inf')
        for driver in Driver.objects.filter(is_available=True):
            driver_location = (driver.latitude, driver.longitude)
            driver_distance = distance(user_location, driver_location).km
            if driver_distance < min_distance:
                min_distance = driver_distance
                nearest_driver = driver

        if nearest_driver:
            ride = Ride.objects.create(
                user=request.user,
                driver=nearest_driver,
                start_location=start_location_string,
                end_location=drop_off_location,
                status="pending",

                # start_latitude=request.POST.get('latitude'),
                # start_longitude=request.POST.get('longitude'),
            )

            ride.save()
            return redirect(ride.get_absolute_url())
        else:
            # Handle case when no driver is available nearby
            messages.error(request, "No driver available")
            return render(request, 'drivers/available_driver.html')


@login_required
def ride_details(request, pk):
    """
    Retrieves and displays details for a specific ride based on the ID.
    """
    notifications = Notification.objects.filter(user=request.user, has_seen=False)
    ride = get_object_or_404(Ride, pk=pk)  # Retrieve ride object or raise 404 for invalid ID
    ride_history = Ride.objects.filter(user=request.user, status="completed")
    context = {
        'ride': ride,
        "notifications": notifications,
        "ride_history": ride_history
    }
    return render(request, 'drivers/ride_details.html', context)


@login_required
@status_check_middleware
def recent_ride(request):
    notifications = Notification.objects.filter(user=request.user, has_seen=False)
    most_recent_ride = Ride.objects.filter(user=request.user,
                                           status="completed").latest('-start_time')
    ride_history = Ride.objects.filter(user=request.user, status="completed")

    # Check if a ride exists
    if not most_recent_ride:
        context = {'error': 'No rides found for this user.'}

    else:
        context = {
            'ride': most_recent_ride,
            "notifications": notifications,
            "ride_history": ride_history,
            'error': 'No rides found for this user.'
        }

    return render(request, 'drivers/ride_details.html', context)


def haversine_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Difference in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = R * c
    return distance

@login_required
def complete_ride(request, pk):
    ride = get_object_or_404(Ride, pk=pk)

    if request.method == 'POST':
        # Assuming the end location details are sent with the request
        ride.end_latitude = request.POST['end_latitude']
        ride.end_longitude = request.POST['end_longitude']
        ride.end_location = request.POST['end_location']

        # Calculate the distance covered
        distance = haversine_distance(ride.start_latitude, ride.start_longitude, ride.end_latitude, ride.end_longitude)
        ride.distance_covered = round(distance, 2)

        # Update ride status to completed
        ride.status = 'completed'
        ride.save()

        return JsonResponse(
            {'status': 'success', 'message': 'Ride completed successfully', 'distance_covered': ride.distance_covered})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def fingerprint_payment(request, ride_id):
    return render(request, 'users/fingerprint_payment.html', {'ride_id': ride_id})


@login_required
@csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        data = request.json()
        ride_id = data.get('ride_id')
        ride = Ride.objects.get(id=ride_id)
        user = ride.user
        wallet = Account.objects.get(user=user)

        try:
            credential_id = data['id']
            raw_id = base64.urlsafe_b64decode(data['rawId'])
            client_data_json = base64.urlsafe_b64decode(data['response']['clientDataJSON'])
            authenticator_data = base64.urlsafe_b64decode(data['response']['authenticatorData'])
            signature = base64.urlsafe_b64decode(data['response']['signature'])

            # Retrieve the public key associated with the user
            # This is a placeholder and should be replaced with actual key retrieval logic
            public_key_pem = b"-----BEGIN PUBLIC KEY-----\n... Your Public Key ...\n-----END PUBLIC KEY-----"

            public_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), public_key_pem)

            # Verify the signature
            public_key.verify(signature, client_data_json + authenticator_data, ec.ECDSA(hashes.SHA256()))

            # If verification succeeds, process the payment
            amount = ride.calculate_cost()

            if wallet.balance >= amount:
                wallet.balance -= amount
                wallet.save()

                # Update ride status
                ride.status = 'completed'
                ride.save()

                return JsonResponse({'status': 'success', 'message': 'Payment successful'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Insufficient balance'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def offline(request):
    return render(request, 'users/offline.html')
