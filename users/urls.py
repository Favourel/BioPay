from django.urls import path
from . import views as user_view

urlpatterns = [
    path("dashboard/", user_view.user_dashboard, name="dashboard"),
    path("process_topUp/", user_view.process_topUp, name="process_topUp"),
    path("search_drivers/", user_view.search_drivers, name="search_drivers"),

    path('book_ride/', user_view.book_ride, name='book_ride'),
    path('ride_details/<uuid:pk>/', user_view.ride_details, name='ride-detail'),
    path('recent-ride/', user_view.recent_ride, name='recent_ride'),

    path('process_payment/<uuid:pk>/', user_view.process_payment, name='process_payment'),
    path('complete_ride/<uuid:pk>/', user_view.complete_ride, name='complete_ride'),
    path('offline/', user_view.offline, name='offline'),
]
