import urllib.request
import json
from django.template.response import TemplateResponse
from apps.program.models import Program
from django.views.generic import DetailView
from django.conf import settings
from socion.info_logs import attestation_logger
from dateutil import parser


class AttestationDetail(DetailView):
    """
    Attestation View for users.
    """
    template_name = 'attestation/trainer.html'
    queryset = Program.objects.all()

    def get(self, request, pk, user_id, role):

        attestation_url = f"{settings.BASE_URL}session/get-attestation-details?role={role}&sessionId={pk}&userId={user_id}&ip-address=106.51.81.14"
        response = urllib.request.urlopen(attestation_url).read().decode('utf-8')
        url = f"{settings.BASE_URL}attestation/{pk}/{user_id}/{role}"
        data = json.loads(response)
        # session_start_date = parser.parse(data['response']['sessionStartDate']).strftime("%a, %d %b, %Y %I:%M %p")
        # session_end_date = parser.parse(data['response']['sessionEndDate']).strftime("%a, %d %b, %Y %I:%M %p")
        attestationDate = parser.parse(data['response']['attestationDate']).strftime("%d-%b-%Y")
        attestation_logger.info('Successfully Fetched Attestation Details for User with User ID : %s' % user_id)
        return TemplateResponse(request, 'attestation/attestation.html',
                                {"data": data['response'], "url": url, "role": role.title(), "attestationDate": attestationDate})
                                 # "session_start_date": session_start_date, "session_end_date": session_end_date})
