import boto3, botocore
from decouple import config
import uuid
import mimetypes


def s3_file_upload(request, bucket_name):

    aws_session = boto3.Session(aws_access_key_id=config('AWS_ACCESS_KEY_ID'), aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'))
    s3 = aws_session.resource('s3')
    for file in request.FILES.getlist('inline[]'):
        filename = file.name.replace(" ", "_")
        file_name = filename.translate({ord(c): "" for c in "!@#$%^&*()[]{};:,/<>?\|`~=+"})
        ext = file.name.split(".")[-1]
        mimetype = mimetypes.MimeTypes().guess_type(file_name)[0]
        try:
            uuId = uuid.uuid1()
            file_key = "%s%s%s%s" % (bucket_name, uuId, ".", ext)
            s3.Bucket(config('AWS_STORAGE_BUCKET_NAME')).put_object(Key=file_key, Body=file, ContentType=mimetype)
            return file_key
        except botocore.exceptions.ClientError as e:
            print("An error occurred because", e.message)
            return False

