from django.urls import path
from . import views

urlpatterns = [
    path('register_driver/', views.register_driver, name='register_driver'),
    path('driver_dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('update_driver_profile/', views.update_driver_profile, name='update_driver_profile'),

    path('available_drivers_json/', views.available_drivers_json, name='available_drivers_json'),

]
