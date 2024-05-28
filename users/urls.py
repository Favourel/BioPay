from django.urls import path
from . import views as user_view

urlpatterns = [
    path("dashboard/", user_view.user_dashboard, name="dashboard"),
    path("process_topUp/", user_view.process_topUp, name="process_topUp"),
    path("search_drivers/", user_view.search_drivers, name="search_drivers"),

    path('book_ride/', user_view.book_ride, name='book_ride'),
    path('ride_details/<uuid:pk>/', user_view.ride_details, name='ride-detail'),

    path('process_payment/<int:ride_id>/', user_view.process_payment, name='process_payment'),

]
