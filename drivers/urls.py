from django.urls import path, re_path
from . import views

urlpatterns = [
    path('register_driver/', views.register_driver, name='register_driver'),
    path('driver_dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('update_driver_profile/', views.update_driver_profile, name='update_driver_profile'),

    path('available_drivers_json/', views.available_drivers_json, name='available_drivers_json'),
    path('delete-account/', views.delete_account, name='delete_account'),
    # re_path(r"^serviceworker\.js$", views.service_worker, name="serviceworker"),
    # re_path(r"^manifest\.json$", views.manifest, name="manifest"),
    # path("offline/", views.offline, name="offline"),
]
