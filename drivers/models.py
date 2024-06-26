from math import sqrt
from django.shortcuts import reverse
from django.conf import settings
from django.db import models
from datetime import datetime
from geopy.geocoders import Nominatim
import uuid


class Driver(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)
    latitude = models.FloatField()
    longitude = models.FloatField()
    # location = gis_models.PointField(geography=True)  # Geospatial field for location
    car_model = models.CharField(max_length=50)
    color = models.CharField(max_length=20)
    is_available = models.BooleanField(default=True)
    driver_picture = models.ImageField(default='profile_picture/edit.png', upload_to='profile_picture')
    date_joined = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.user.username} ({self.car_model})"


class Ride(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    start_location = models.CharField(max_length=100)
    end_location = models.CharField(max_length=100, blank=True, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    start_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    start_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    end_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    end_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    distance_covered = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Distance in kilometers

    fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'),
                                                      ('completed', 'Completed')], default='pending')

    def __str__(self):
        return (f"Ride from {self.start_location} to {self.end_location} "
                f"requested by {self.user.username} (Status: {self.status})")

    class Meta:
        ordering = ['-start_time']

    def get_absolute_url(self):
        return reverse("ride-detail", kwargs={"pk": self.id})

    def calculate_cost(self):
        # Example cost calculation
        base_fare = 500.00
        distance_fare = 2.00 * self.calculate_distance()
        return base_fare + distance_fare

    def calculate_distance(self):
        # Use geopy to calculate distance
        geolocator = Nominatim(user_agent="drivers")  # Replace with your app name

        start_location_geocode = geolocator.geocode(self.start_location)
        end_location_geocode = geolocator.geocode(self.end_location)

        if start_location_geocode and end_location_geocode:
            start_latitude = start_location_geocode.latitude
            start_longitude = start_location_geocode.longitude
            end_latitude = end_location_geocode.latitude
            end_longitude = end_location_geocode.longitude

            # Use a distance calculation formula (e.g., Haversine formula)
            from math import radians, sin, cos, acos

            start_lat_rad = radians(start_latitude)
            end_lat_rad = radians(end_latitude)
            delta_lat = radians(end_latitude - start_latitude)
            delta_lon = radians(end_longitude - start_longitude)

            a = sin(delta_lat / 2) * sin(delta_lat / 2) + cos(start_lat_rad) * cos(end_lat_rad) * sin(delta_lon / 2) * sin(delta_lon / 2)
            c = 2 * acos(sqrt(a))

            # Earth radius in kilometers (you can adjust the unit if needed)
            earth_radius = 6371

            distance = earth_radius * c
            return distance
        else:
            # Handle cases where geocoding fails (e.g., invalid addresses)
            return 0  # Or set a default distance
