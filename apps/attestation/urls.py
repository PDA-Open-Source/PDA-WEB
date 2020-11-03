from django.urls import path
from apps.attestation.views import AttestationDetail
from . import views

urlpatterns = [
    path("<int:pk>/<slug:user_id>/<slug:role>", AttestationDetail.as_view(), name="attestation-detail"),
    path("download-attestation/", views.attestation_download, name='download-attestation'),
]
