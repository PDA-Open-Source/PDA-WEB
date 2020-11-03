from django.shortcuts import render
import boto3, botocore
from decouple import config
from django.conf import settings
from pda.info_logs import authentication_logger
import base64
import mimetypes
import botocore
import boto3.session
import urllib.parse
from pda.info_logs import program_logger
from django.http import JsonResponse

URL = settings.AWS_STATIC_URL


def login(request):
    return render(request, 'authentication/login.html')


def signup_request_otp(request):
    return render(request, 'authentication/signup-request-otp.html')


def signup_create_password(request):
    return render(request, 'authentication/signup-create-password.html')


def forgot_password(request):
    return render(request, 'authentication/forgot-password.html')


def reset_password(request):
    return render(request, 'authentication/reset-password.html')


def landing(request):
    return render(request, 'authentication/landing-page.html')


def user_profile(request):
    return render(request, 'authentication/user-profile.html')


def about_us(request):
    return render(request, 'authentication/about-us.html')


def privacy_policy(request):
    return render(request, 'authentication/privacy-policy.html')


def terms_and_conditions(request):
    return render(request, 'authentication/terms-and-conditions.html')


def upload_profile_pic(request):

    aws_access_key_id = config('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = config('AWS_SECRET_ACCESS_KEY')
    bucket_name = config('AWS_STORAGE_BUCKET_NAME')
    aws_session = boto3.Session(aws_access_key_id, aws_secret_access_key)
    s3 = aws_session.resource('s3')
    try:
        if request.POST:
            ext = request.POST.get('ext')
            file_as_base64 = request.POST.get('image')
            base64_url = file_as_base64[file_as_base64.find(",")+1:]
            file = base64.b64decode(base64_url)
            filename = "%s%s%s%s" % ("profile-picture/", request.user.user_id, ".", ext)
            s3.Bucket(bucket_name).put_object(Key=filename, Body=file, ContentType=f'image/{ext}', CacheControl='no-cache')
        authentication_logger.info('Profile Picture Uploaded Successfully.')
        return render(request, 'authentication/user-profile.html')
    except botocore.exceptions.ClientError as e:
        print("An error occurred because", e.message)
        authentication_logger.error('Could not Upload Profile Picture as %s.' % e.message)
        return render(request, 'authentication/user-profile.html')

def profile_download(request):
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
