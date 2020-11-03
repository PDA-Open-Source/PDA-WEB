from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('signup-request-otp/', views.signup_request_otp, name='signup-request-otp'),
    path('signup-create-password/', views.signup_create_password, name='signup-create-password'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('reset-password/', views.reset_password, name='reset-password'),
    path('landing/', views.landing, name='landing'),
    path('user-profile/', views.user_profile, name='user-profile'),
    path('about-us/', views.about_us, name='about-us'),
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    path('terms-conditions/', views.terms_and_conditions, name='terms-and-conditions'),
    path('upload-profile-pic/', views.upload_profile_pic, name='upload-profile-pic'),
    path('', RedirectView.as_view(pattern_name='login', permanent=False)),
    path("download-profile/", views.profile_download, name='download-profile'),
]
