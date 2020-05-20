from django.urls import path
from apps.attestation.views import AttestationDetail

urlpatterns = [
    path("<int:pk>/<slug:user_id>/<slug:role>", AttestationDetail.as_view(), name="attestation-detail"),
]
