from django.shortcuts import render
import boto3, botocore
from decouple import config
from django.conf import settings
from socion.info_logs import authentication_logger
import base64
import mimetypes

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
