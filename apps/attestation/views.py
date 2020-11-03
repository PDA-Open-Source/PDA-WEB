import urllib.request
import json
from django.template.response import TemplateResponse
from apps.program.models import Program
from django.views.generic import DetailView
from django.conf import settings
from pda.info_logs import attestation_logger
from dateutil import parser
import botocore
import boto3.session
import urllib.parse
from pda.info_logs import program_logger
from django.http import JsonResponse
from decouple import config
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

def attestation_download(request):
    data = dict()
    if request.method == "POST":
        session = boto3.session.Session(region_name=config('AWS_REGION_NAME'))
        s3 = session.client('s3', aws_access_key_id=config('AWS_ACCESS_KEY_ID'), aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'))
        download_url = request.POST['content_url']
        filename = urllib.parse.quote(request.POST['content_name'])
        path = download_url.replace(config('aws_s3_url_private'), "")
        try:
            response = s3.generate_presigned_url('get_object',
                                                 Params={'Bucket': config('aws_s3_bucket_name_private'), 'Key': path, 'ResponseContentDisposition': "attachment; filename=%s" % filename},
                                                 ExpiresIn=3000)
            data['downloaded'] = True
            data['file_url'] = response
            program_logger.info('Successfully Downloaded a Document.')
            return JsonResponse(data)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
                data['downloaded'] = False
                program_logger.error('The object does not exist.')
                return JsonResponse(data)
            else:
                data['downloaded'] = False
                program_logger.error('Error while Downloading Document.')
                return JsonResponse(data)
