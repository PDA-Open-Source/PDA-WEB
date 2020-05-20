from django.urls import path

from . import views

urlpatterns = [
    path('scanner/', views.scanner, name='scanner'),
    path('notification/', views.notification, name='notification'),
    path('error/', views.error_page, name='error'),
    path('inscanner/', views.inscanner, name='inscanner'),
]