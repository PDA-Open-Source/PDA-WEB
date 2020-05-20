import csv
from django.utils.encoding import smart_str
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, View, RedirectView, CreateView, FormView
from apps.entity.models import Entity, Entity_Role
from apps.program.models import Program, Topic, Content, Program_Roles, ProgramDocument
from core.models import Session, Session_Links
from .forms import ProgramForm, TopicForm, TopicUpdateForm, TopicUpdateForm1, ContentForm
from socion.storage_backends import s3_file_upload
import vimeo
from decouple import config
import requests
from datetime import datetime
from django.db.models import Prefetch
import psycopg2
from core.views import Notifications
from socion.info_logs import program_logger
from dateutil import parser
import botocore
import boto3.session
import uuid
import mimetypes
import urllib.parse
import xlwt


BASE_DIR = settings.PROJECT_DIR
URL = settings.AWS_STATIC_URL


def pop_add_admin(template_name, request, **kwargs):
    data = dict()
    context = None
    qr_value = kwargs.get('qr_value', None)
    if qr_value is not None:
        context = {'qr_value': qr_value}
    if request.method == 'POST':
        user_id = request.POST.get('userId')
        role = request.POST.get('programRole')
        program_id = request.POST.get('programId')
        admin_user_name = request.POST.get('adminUserName')
        add_member_url = f"{settings.BASE_URL}entity/program/{program_id}/roles/"
        payload = {
            "userIds": [str(user_id)],
            "programId": program_id,
            "role": str(role),
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.post(add_member_url, json=payload, headers=headers)
        response_result = response.json()
        if response_result['responseCode'] == 200:
            program = Program.objects.get(pk=program_id)
            admin_ids = list()
            title = ""
            description = ""
            notification_roles = list()
            if role == settings.SOCION_PROGRAM_ADMIN:
                title = "Add Program Admin"
                description = f"{admin_user_name} has been onboarded as a Program Administrator to the Program {program.name}"
                admin_ids = list(Entity_Role.objects.values_list("user_id", flat=True).filter(role=settings.SOCION_ENTITY_ADMIN, entity_id=program.entity_id, deleted=False).distinct())
                notification_roles = [settings.SOCION_PROGRAM_ADMIN, ]
            elif role == settings.SOCION_CONTENT_ADMIN:
                title = "Add Content Admin"
                description = f"{admin_user_name} has been onboarded as a Content  Administrator to the Program {program.name}"
                notification_roles = [settings.SOCION_PROGRAM_ADMIN, settings.SOCION_CONTENT_ADMIN, ]
            elif role == settings.SOCION_TRAINER:
                title = "Add Trainer"
                description = f"{admin_user_name} has been onboarded as a Trainer to the Program {program.name}"
                notification_roles = [settings.SOCION_PROGRAM_ADMIN, settings.SOCION_TRAINER, ]
            program_member_admin_ids = list(Program_Roles.objects.values_list("user_id", flat=True).filter(role__in=notification_roles, program_id=program_id, deleted=False).distinct())
            net_admin_ids = list(set().union(admin_ids, program_member_admin_ids))
            if net_admin_ids:
                for admin_user_id in net_admin_ids:
                    Notifications.notification_save(title=title,
                                                    description=description,
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=None, user_id=admin_user_id, session_id=None)
            program_logger.info('Added Admin Successfully to the Program with ID : %s.' % program_id)
            data['form_is_valid'] = True
        else:
            program_logger.error('Could not add Admin to the Program with ID : %s.' % program_id)
            data['form_is_valid'] = False
    data['html_form'] = render_to_string(template_name, context=context, request=request)
    return JsonResponse(data)


def add_admin(request):
    return pop_add_admin('program/detail/add-admin.html', request)


def add_admin_info(request, qr_value):
    if request.method == 'POST':
        return pop_add_admin('program/detail/add-admin-info.html', request, qr_value=qr_value)
    else:
        return pop_add_admin('program/detail/add-admin-info.html', request, qr_value=qr_value)


class ProgramList(ListView):
    """
    List view of program for trainer.
    """
    template_name = "program/list/program_list.html"
    queryset = Program.objects.all()
    context_object_name = 'program'

    def get_queryset(self, **kwargs):
        user_id = self.request.user.user_id
        if settings.SOCION_SUPER_ADMIN in self.request.user.roles:
            return super().get_queryset().order_by('deleted')
        else:
            entity_ids = list(Entity_Role.objects.values_list("entity_id", flat=True).filter(user_id=user_id, deleted=False))
            programs_id_from_entity = Program.objects.values_list("id", flat=True).filter(entity_id__in=entity_ids)
            program_id_program_admin = list(Program_Roles.objects.values_list("program_id", flat=True).filter(user_id=user_id, role=settings.SOCION_PROGRAM_ADMIN, deleted=False))
            program_id_content_admin = list(Program_Roles.objects.values_list("program_id", flat=True).filter(user_id=user_id, role=settings.SOCION_CONTENT_ADMIN, deleted=False))
            program_id_trainer = list(Program_Roles.objects.values_list("program_id", flat=True).filter(user_id=user_id, role=settings.SOCION_TRAINER, deleted=False))
            net_program_ids = set().union(program_id_program_admin, program_id_content_admin, program_id_trainer, programs_id_from_entity)
            return super().get_queryset().filter(pk__in=net_program_ids).order_by('deleted')


class ProgramMixin(UserPassesTestMixin):

    def test_func(self):
        if not self.request.is_logged_in:
            return None

        user_id = self.request.user.user_id
        pk = self.kwargs[self.pk_url_kwarg]
        socion_roles = list(
            Program_Roles.objects.values_list("role", flat=True).filter(user_id=user_id, program_id=pk, deleted=False).distinct()
        )
        socion_program_admin_roles = list(
            Program_Roles.objects.values_list("role", flat=True).filter(user_id=user_id, program_id=pk, role=settings.SOCION_PROGRAM_ADMIN).distinct()
        )
        program_detail = Program.objects.get(pk=pk)
        entity_id = program_detail.entity.id
        entity_role = list(
            Entity_Role.objects.values_list("role", flat=True).filter(user_id=user_id, entity_id=entity_id,
                                                                      deleted=False).distinct()
        )
        socion_roles.extend(entity_role)
        if settings.SOCION_SUPER_ADMIN not in self.request.user.roles:
            if socion_roles or socion_program_admin_roles:
                return True
            else:
                return False
        else:
            return True

    def handle_no_permission(self):
        if not self.request.is_logged_in:
            return redirect(settings.LOGIN_URL)
        else:
            return redirect(settings.ERROR_PAGE_URL)


class ProgramDetail(ProgramMixin, DetailView):
    """
    Detail view of program for trainer.
    """
    model = Program
    template_name = 'program/detail/index.html'
    context_object_name = 'program'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        user_id = self.request.user.user_id
        members = list()
        attestations = list()
        pk = self.kwargs.get(self.pk_url_kwarg)
        context = super().get_context_data(**kwargs)
        entity_id = context["program"].entity.id
        context["documents"] = ProgramDocument.objects.filter(program_id=pk, deleted=False)
        context["contents"] = Topic.objects.filter(program_id=pk).prefetch_related(Prefetch(
                                                                    'contents',
                                                                    queryset=Content.objects.filter(deleted=False)))
        completed_session = list()
        upcoming_session = list()
        session_id_list = list()
        sessions = list()

        try:
            topic_ids = Topic.objects.values_list('id', flat=True).filter(program_id=pk)
            connection = psycopg2.connect(user=settings.SESSION_DB_USER,
                                          password=settings.SESSION_DB_PASSWORD,
                                          host=settings.SESSION_DB_HOST,
                                          port=settings.SESSION_DB_PORT,
                                          database=settings.SESSION_DB_NAME)
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            program_logger.info('Successfully connected to the Session Database.')
            query = "SELECT * FROM session WHERE topic_id IN ({})".format(",".join([str(i) for i in topic_ids]))
            cursor.execute(query, topic_ids)
            sessions = cursor.fetchall()
            if connection:
                cursor.close()
                connection.close()
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
            pass

        try:
            context['session_list'] = list(sessions)
            for sessions_items in context['session_list']:
                start_date = datetime.strptime(sessions_items['session_start_date'], '%Y-%m-%d %H:%M:%S.%f')
                end_date = datetime.strptime(sessions_items['session_end_date'], '%Y-%m-%d %H:%M:%S.%f')
                sessions_items.update(session_start_date=start_date)
                sessions_items.update(session_end_date=end_date)
                session_id = sessions_items['id']
                session_id_list.append(session_id)
                if sessions_items['session_end_date'].replace(tzinfo=None) > datetime.now().replace(tzinfo=None):
                    upcoming_session.append(sessions_items)
                else:
                    completed_session.append(sessions_items)
            attestation_list_url = f"{settings.BASE_URL}session/numberofattestationspersession"
            request_body = {
                "sessionIds": session_id_list
            }
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            attestation_response = requests.post(attestation_list_url, json=request_body, headers=headers)
            if attestation_response.status_code == 200:
                attestations = attestation_response.json()
                program_logger.info('Successfully Fetched Number of Attestations for the Program with ID : %s.' % pk)
            for attestation in attestations:
                for upcoming_session_index in range(len(upcoming_session)):
                    if attestation['sessionId'] == upcoming_session[upcoming_session_index]['id']:
                        upcoming_session[upcoming_session_index].update(upcoming_session_contents=Content.objects.filter(topic_id=upcoming_session[upcoming_session_index]['topic_id'], deleted=False))
                        upcoming_session[upcoming_session_index].update(upcoming_session_links=Session_Links.objects.using('session_db').filter(session_id=attestation['sessionId']))
                        upcoming_session[upcoming_session_index].update(participant_count=attestation['membersCount'])
                for completed_session_index in range(len(completed_session)):
                    if attestation['sessionId'] == completed_session[completed_session_index]['id']:
                        completed_session[completed_session_index].update(completed_session_contents=Content.objects.filter(topic_id=completed_session[completed_session_index]['topic_id'], deleted=False))
                        completed_session[completed_session_index].update(completed_session_links=Session_Links.objects.using('session_db').filter(session_id=attestation['sessionId']))
                        completed_session[completed_session_index].update(attestation_count=attestation['attestationCount'])
                        completed_session[completed_session_index].update(participant_count=attestation['participantCount'])
            context['upcoming_session'] = upcoming_session
            context['completed_session'] = completed_session
        except (Exception, ValueError) as error:
            print("Error while retrieving session list.", error)
            program_logger.error('Could not Fetch Number of Attestations for the Program with ID : %s.' % pk)
            pass

        member_list_url = f"{settings.BASE_URL}entity/program/members?programId={pk}&entityId=31"
        program_role = list(
            Program_Roles.objects.values_list("role", flat=True).filter(user_id=user_id, program_id=pk, deleted=False).distinct()
        )
        entity_role = list(
            Entity_Role.objects.values_list("role", flat=True).filter(user_id=user_id, entity_id=entity_id, deleted=False).distinct()
        )
        program_role.extend(entity_role)
        response = requests.get(member_list_url)
        if response.status_code == 200:
            members = response.json()
            program_logger.info('Fetched List of Members Successfully for the Program with ID : %s.' % pk)
        program_admin = list()
        content_admin = list()
        trainer = list()
        other = list()
        for item in members:
            if item['role'] == settings.SOCION_PROGRAM_ADMIN:
                program_admin.append(item)
            elif item['role'] == settings.SOCION_CONTENT_ADMIN:
                content_admin.append(item)
            elif item['role'] == settings.SOCION_TRAINER:
                trainer.append(item)
            else:
                other.append(item)
        context['PROGRAM_ADMIN'] = sorted(program_admin, key=lambda i: i['deactivated'])
        context['PROGRAM_ADMIN_ACTIVE_COUNT'] = len(list(filter(lambda i: i['deactivated'] is False, program_admin)))
        context['CONTENT_ADMIN'] = sorted(content_admin, key=lambda i: i['deactivated'])
        context['CONTENT_ADMIN_ACTIVE_COUNT'] = len(list(filter(lambda i: i['deactivated'] is False, content_admin)))
        context['TRAINER'] = sorted(trainer, key=lambda i: i['deactivated'])
        context['TRAINER_ACTIVE_COUNT'] = len(list(filter(lambda i: i['deactivated'] is False, trainer)))
        context['OTHER'] = sorted(other, key=lambda i: i['deactivated'])
        context['MEMBERS'] = sorted(members, key=lambda i: i['deactivated'])

        if settings.SOCION_SUPER_ADMIN not in self.request.user.roles:

            if settings.SOCION_ENTITY_ADMIN in program_role:
                context["entity_permissions"] = settings.ENTITY_PERMISSIONS
            if settings.SOCION_PROGRAM_ADMIN in program_role:
                context["permissions"] = settings.PROGRAM_PERMISSIONS
                context["permission_can_view_participant_list"] = True
            elif settings.SOCION_CONTENT_ADMIN in program_role:
                context["permissions"] = settings.CONTENT_PERMISSIONS
            elif settings.SOCION_TRAINER in program_role:
                context["permissions"] = settings.TRAINER_PERMISSIONS

        return context


def csv_download(request, pk):
    context = dict()
    session = Session.objects.using('session_db').get(pk=pk)
    participant_list_url = f"{settings.BASE_URL}session/get-participant-list/{session.id}"
    response = requests.get(participant_list_url)
    if response.status_code == 200:
        data = response.json()
        response_data = data['response']
        context = {
            'participants': response_data['participants'],
            'members': response_data['members']
        }

    filename = (urllib.parse.quote(session.session_name) + "_" + datetime.now().strftime("%Y-%m-%d %H-%M-%S"))
    # response content type
    # response = HttpResponse(content_type='text/csv')  # csv
    response = HttpResponse(content_type='application/ms-excel')  # excel
    response['Content-Disposition'] = f'attachment; filename="{filename}.xls"'  # .xls for excel & .csv for csv
    # # for csv
    # csv_writer = csv.writer(response, csv.excel)
    # response.write(u'\ufeff'.encode('utf8'))
    # csv_writer.writerow(
    #     [smart_str(u'Session Name'),
    #      smart_str(u'Session Start Date'),
    #      smart_str(u'Session End Date'),
    #      smart_str(u'Session Venue'),
    #      smart_str(u'Participant Name'),
    #      smart_str(u'Participant Phone Number'),
    #      smart_str(u'Participant EmailId'),
    #      smart_str(u'Participant Scan-In Time'),
    #      smart_str(u'Participant Scan-Out Time'),
    #      smart_str(u'Attestation Generated'),
    #      ])
    # for participant in participants:
    #     csv_writer.writerow([
    #         smart_str(session.session_name),
    #         smart_str(parser.parse(session.session_start_date).strftime("%d-%m-%Y %H:%M:%S")),
    #         smart_str(parser.parse(session.session_end_date).strftime("%d-%m-%Y %H:%M:%S")),
    #         smart_str(session.address),
    #         smart_str(participant['name']),
    #         smart_str(user_phone_number(participant['phoneNumber'], participant['countryCode'])),
    #         smart_str(participant['emailId']),
    #         smart_str(participant['scanInTime']),
    #         smart_str(participant['scanOutTime']),
    #         smart_str(attestation_status(participant['attestationGenerated']))
    #      ])

    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    # adding sheet
    ws = wb.add_sheet("Participants")

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True

    # column header names, you can use your own headers here
    columns = ['Session Name', 'Session Start Date', 'Session End Date', 'Session Venue', 'Participant Name',
               'Participant Phone Number', 'Participant EmailId', 'Participant Scan-In Time',
               'Participant Scan-Out Time', ]
               # 'Attestation Generated', ]

    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    # get your data, from database or from a text file...
    for participant in context['participants']:
        row_num = row_num + 1
        ws.write(row_num, 0, session.session_name, font_style)
        ws.write(row_num, 1, parser.parse(session.session_start_date).strftime("%d-%b-%Y %H:%M:%S"), font_style)
        ws.write(row_num, 2, parser.parse(session.session_end_date).strftime("%d-%b-%Y %H:%M:%S"), font_style)
        ws.write(row_num, 3, session.address, font_style)
        ws.write(row_num, 4, participant['name'], font_style)
        ws.write(row_num, 5, user_phone_number(participant['phoneNumber'], participant['countryCode']), font_style)
        ws.write(row_num, 6, participant['emailId'], font_style)
        ws.write(row_num, 7, scan_time_status(participant['scanInTime']), font_style)
        ws.write(row_num, 8, scan_time_status(participant['scanOutTime']), font_style)
        # ws.write(row_num, 9, attestation_status(participant['attestationGenerated']), font_style)

    # adding sheet
    ws = wb.add_sheet("Members")

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True

    columns = ['Session Name', 'Session Start Date', 'Session End Date', 'Session Venue', 'Member Name', 'Member Role',
               'Member Phone Number', 'Member EmailId', ]

    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    # get your data, from database or from a text file...
    for member in context['members']:
        row_num = row_num + 1
        ws.write(row_num, 0, session.session_name, font_style)
        ws.write(row_num, 1, parser.parse(session.session_start_date).strftime("%d-%b-%Y %H:%M:%S"), font_style)
        ws.write(row_num, 2, parser.parse(session.session_end_date).strftime("%d-%b-%Y %H:%M:%S"), font_style)
        ws.write(row_num, 3, session.address, font_style)
        ws.write(row_num, 4, member['name'], font_style)
        ws.write(row_num, 5, user_role_as_string(member['role']), font_style)
        ws.write(row_num, 6, user_phone_number(member['phoneNumber'], member['countryCode']), font_style)
        ws.write(row_num, 7, member['emailId'], font_style)

    wb.save(response)
    program_logger.info('Successfully Downloaded Participant List for Session with ID : %s' % session.id)
    return response


def user_role_as_string(user_role):
    if user_role:
        role_str = ", ".join(user_role).title()
    else:
        role_str = ""
    return role_str


def attestation_status(attestation_val):
    if attestation_val:
        return "YES"
    else:
        return "NO"


def scan_time_status(scan_time_val):
    if scan_time_val:
        return parser.parse(scan_time_val).strftime("%d-%b-%Y %H:%M:%S")
    else:
        return "N/A"


def user_phone_number(phone_number, country_code):
    if country_code != "":
        return country_code + "-" + phone_number
    else:
        return phone_number


def get_participant_list(request, pk):
    context = dict()
    session = Session.objects.using('session_db').get(pk=pk)
    participant_list_url = f"{settings.BASE_URL}session/get-participant-list/{session.id}"
    try:
        response = requests.get(participant_list_url)
        if response.status_code == 200:
            data = response.json()
            response_data = data['response']
            context = {
                'session': session,
                'participants': response_data['participants'],
                'members': response_data['members'],
                'contents': response_data['contents']
            }
            program_logger.info('Successfully Fetched Participant List for Session with ID : %s' % session.id)
        return render(request, 'program/detail/participant_list_new.html', context)
    except Exception as error:
        program_logger.error('Could not fetch participant list for Session because %s.' % error)
        pass


class CreateProgram(View):

    def get(self, request, pk=None):
        entity = get_object_or_404(Entity, pk=pk)
        try:
            form = ProgramForm()
            template = 'program/list/program_create.html'
            return save_all(request, form=form, template_name=template, instance=entity)

        except ValueError:
            return HttpResponseRedirect(reverse('program-list'))

    def post(self, request, pk):
        entity = get_object_or_404(Entity, pk=pk)
        try:
            if request.method == 'POST':
                form = ProgramForm(request.POST, request.FILES)
                template = 'program/list/program_create.html'
                return save_all(request, form=form, template_name=template, instance=entity)
        except ValueError:
            return False


def save_all(request, form, template_name, instance):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user.user_id
            obj.entity_id = instance.id
            obj.save()
            entity_admin_ids = list(Entity_Role.objects.values_list("user_id", flat=True).filter(role=settings.SOCION_ENTITY_ADMIN, entity_id=instance.id, deleted=False).distinct())
            entity_admin_ids.append(request.user.user_id)
            if request.FILES:
                aws_session = boto3.Session(aws_access_key_id=config('AWS_ACCESS_KEY_ID'), aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'))
                s3 = aws_session.resource('s3')
                for file in request.FILES.getlist('inline[]'):
                    program_id = obj.id
                    ext = file.name.split(".")[-1]
                    mimetype = mimetypes.MimeTypes().guess_type(file.name)[0]
                    uuId = uuid.uuid1()
                    if ext in settings.SOCION_VIDEO_FORMAT:
                        v = vimeo.VimeoClient(token=config('VIMEO_ACCESS_TOKEN'))
                        path = file.temporary_file_path()
                        try:
                            # Upload the file and include the video title and description.
                            uri = v.upload(path, data={
                                'name': file.name,
                                'chunk_size': 128 * 1024 * 1024
                                })

                            # Get the metadata response from the upload and log out the Vimeo.com url
                            video_data = v.get(uri + '?fields=link').json()
                            vimeo_url = video_data['link']
                            file_key = "%s%s%s%s" % ("Program-Docs/Program Videos/", uuId, ".", ext)
                            s3.Bucket(config('AWS_STORAGE_BUCKET_NAME')).put_object(Key=file_key, Body=file, ContentType=mimetype)
                            url = "%s%s" % (URL, file_key)
                            attachment = ProgramDocument(program_id=program_id, name=file,
                                                         content_url=url, vimeo_url=vimeo_url,
                                                         created_by=request.user.user_id, content_type='Video')
                            attachment.save()
                            program_logger.info('Successfully Added a Video to a Program with ID : %s.' % program_id)

                        except vimeo.exceptions.VideoUploadFailure as e:

                            print('Error uploading %s' % file.name)
                            print('Server reported: %s' % e.message)
                            program_logger.error('Could not upload a video to a program because %s.' % e)
                            pass

                    elif ext in settings.SOCION_IMAGE_FORMAT:
                        file_key = "%s%s%s%s" % ("Program-Docs/Images/", uuId, ".", ext)
                        s3.Bucket(config('AWS_STORAGE_BUCKET_NAME')).put_object(Key=file_key, Body=file, ContentType=mimetype)
                        url = "%s%s" % (URL, file_key)
                        attachment = ProgramDocument(program_id=program_id, name=file, content_url=url,
                                                     created_by=request.user.user_id, content_type='Image')
                        attachment.save()
                        program_logger.info('Successfully Added an Image to a Program with ID : %s.' % program_id)
                    elif ext in settings.SOCION_DOC_FORMAT:
                        file_key = "%s%s%s%s" % ("Program-Docs/Documents/", uuId, ".", ext)
                        s3.Bucket(config('AWS_STORAGE_BUCKET_NAME')).put_object(Key=file_key, Body=file, ContentType=mimetype)
                        url = "%s%s" % (URL, file_key)
                        attachment = ProgramDocument(program_id=program_id, name=file, content_type='Document',
                                                     created_by=request.user.user_id, content_url=url)
                        attachment.save()
                        program_logger.info('Successfully Added a Document to a Program with ID : %s.' % program_id)
                if entity_admin_ids:
                    for entity_user_id in entity_admin_ids:
                        Notifications.notification_save(title='Document Upload',
                                                        description=f"New Document(s) have been uploaded to Program {obj.name}.",
                                                        notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                        date_time=datetime.now(), is_deleted=False, is_read=False,
                                                        role=None, user_id=entity_user_id, session_id=None)
            data['form_is_valid'] = True
            program_logger.info('Successfully Created a Program.')
            if entity_admin_ids:
                for entity_user_id in entity_admin_ids:
                    Notifications.notification_save(title='Create Program',
                                                    description=f"Program {obj.name} has been created",
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=None, user_id=entity_user_id, session_id=None)
        else:
            program_logger.error('Could not Add a program as form validation failed.')
            data['form_is_valid'] = False
    context = {'form': form, 'entity': instance}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


class UpdateProgram(RedirectView):

    def get(self, request, pk):
        context = dict()
        user_id = request.user.user_id
        program = get_object_or_404(Program, pk=pk)
        entity_id = program.entity.id
        form = ProgramForm(instance=program)
        program_role = list(
            Program_Roles.objects.values_list("role", flat=True).filter(user_id=user_id, program_id=pk,
                                                                        deleted=False).distinct()
        )
        entity_role = list(
            Entity_Role.objects.values_list("role", flat=True).filter(user_id=user_id, entity_id=entity_id,
                                                                      deleted=False).distinct()
        )
        program_role.extend(entity_role)
        if settings.SOCION_SUPER_ADMIN in request.user.roles:
            context["admin_permissions"] = True
        else:
            if settings.SOCION_ENTITY_ADMIN in program_role:
                context["entity_permissions"] = settings.ENTITY_PERMISSIONS
            if settings.SOCION_PROGRAM_ADMIN in program_role:
                context["permissions"] = settings.PROGRAM_PERMISSIONS

        template = 'program/detail/program_update.html'
        return update_all(request, form=form, template_name=template, permissions=context)

    def post(self, request, pk):
        program = get_object_or_404(Program, pk=pk)
        try:
            form = ProgramForm(request.POST, instance=program)
            template = 'program/detail/program_update.html'
            return update_all(request, form=form, template_name=template)

        except ValueError:
            return HttpResponseRedirect(reverse('program-detail', kwargs={'pk': pk}))


def count_of_values_changed(old_object, new_object):
    count = 0
    if old_object.name != new_object['name']:
        count = count + 1
    if old_object.description != new_object['description']:
        count = count + 1
    if old_object.start_date != parser.parse(str(new_object['start_date'])):
        count = count + 1
    if old_object.end_date != parser.parse(str(new_object['end_date'])):
        count = count + 1
    if old_object.user_limit != int(new_object['user_limit']):
        count = count + 1
    return count


def update_all(request, form, template_name, permissions=None):
    data = dict()
    description = f"Program details of {form.instance.name} has been changed"
    title = "Edit Program description"
    if request.method == 'POST':
        program = Program.objects.get(pk=form.instance.pk)
        POST = request.POST.copy()
        if settings.SOCION_SUPER_ADMIN in request.user.roles:
            if count_of_values_changed(program, POST) > 1:
                title = "Edit Program Details"
                description = f"The details of Program {form.instance.name} has been changed"
            elif program.name != POST['name']:
                title = "Edit Program name"
                description = f"The name of Program {form.instance.name} has been changed"
            elif program.description != POST['description']:
                title = "Edit Program description"
                description = f"The description for Program {form.instance.name} has been changed"
            elif program.start_date != parser.parse(POST['start_date']):
                title = "Edit Program start date"
                description = f"The start date for Program {form.instance.name} has been changed"
            elif program.end_date != parser.parse(POST['end_date']):
                title = "Edit Program end date"
                description = f"The end date for Program {form.instance.name} has been changed"
            elif program.user_limit != int(POST['user_limit']):
                title = "Edit Program user limit"
                description = f"The user limit of Program {form.instance.name} has been changed"

        if settings.SOCION_SUPER_ADMIN not in request.user.roles:
            description = f"The description for Program {form.instance.name} has been changed"
            POST['name'] = form.instance.name
            POST['start_date'] = form.instance.start_date
            POST['end_date'] = form.instance.end_date
            POST['user_limit'] = form.instance.user_limit
            form = ProgramForm(POST, instance=form.instance)

        program_admin_ids = list(Program_Roles.objects.values_list("user_id", flat=True).filter(role=settings.SOCION_PROGRAM_ADMIN, program_id=form.instance.id, deleted=False).distinct())
        entity_admin_ids = list(Entity_Role.objects.values_list("user_id", flat=True).filter(entity_id=program.entity_id, deleted=False).distinct())
        net_admin_ids = list(set().union(entity_admin_ids, program_admin_ids))
        net_admin_ids.append(program.created_by)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.updated_by = request.user.user_id
            obj.save()
            data['form_is_valid'] = True
            program_logger.info('Successfully Updated a Program with ID : %s.' % form.instance.id)
            if count_of_values_changed(program, POST) != 0:
                if net_admin_ids:
                    for admin_user_id in net_admin_ids:
                        Notifications.notification_save(title=title,
                                                        description=description,
                                                        notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                        date_time=datetime.now(), is_deleted=False, is_read=False,
                                                        role=None, user_id=admin_user_id, session_id=None)
        else:
            program_logger.error('Could not update a Program with ID : %s.' % form.instance.id)
            data['form_is_valid'] = False
    context = {'form': form, 'access': permissions}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


class DeleteProgram(View):

    def get(self, request, pk):
        program = Program.objects.get(pk=pk)
        if Program.delete(request, pk=pk):
            program_admin_ids = list(
                Program_Roles.objects.values_list("user_id", flat=True).filter(program_id=pk, deleted=False).distinct())
            entity_admin_ids = list(
                Entity_Role.objects.values_list("user_id", flat=True).filter(entity_id=program.entity_id,
                                                                             deleted=False).distinct())
            net_admin_ids = list(set().union(entity_admin_ids, program_admin_ids))
            net_admin_ids.append(program.created_by)
            topics = Topic.objects.filter(program_id=pk)
            roles = Program_Roles.objects.values_list("role", flat=True).filter(program_id=pk)
            topics.update(deleted=True)
            roles.update(deleted=True)
            if net_admin_ids:
                for admin_user_id in net_admin_ids:
                    Notifications.notification_save(title="Program deactivate",
                                                    description=f"Program {program.name} has been deactivated",
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=None, user_id=admin_user_id, session_id=None)
            program_logger.info('Successfully Deleted a Program with ID : %s.' % pk)
            return HttpResponseRedirect(reverse('entity-profile', kwargs={'pk': program.entity_id}))
        else:
            program_logger.error('Could not Delete a Program with ID : %s.' % pk)
            return HttpResponseRedirect(reverse('program-detail', kwargs={'pk': pk}))


class ReactivateProgram(View):

    def get(self, request, pk):
        program = Program.objects.get(pk=pk)
        if Program.reactivate(request, pk=pk):
            program_admin_ids = list(
                Program_Roles.objects.values_list("user_id", flat=True).filter(program_id=pk, deleted=False).distinct())
            entity_admin_ids = list(
                Entity_Role.objects.values_list("user_id", flat=True).filter(entity_id=program.entity_id,
                                                                             deleted=False).distinct())
            net_admin_ids = list(set().union(entity_admin_ids, program_admin_ids))
            net_admin_ids.append(program.created_by)
            if net_admin_ids:
                for admin_user_id in net_admin_ids:
                    Notifications.notification_save(title="Program reactivate",
                                                    description=f"Program {program.name} has been reactivated",
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=None, user_id=admin_user_id, session_id=None)
            program_logger.info('Successfully Reactivated a Program with ID : %s.' % pk)
            return HttpResponseRedirect(reverse('program-detail', kwargs={'pk': pk}))
        else:
            program_logger.error('Could not Reactivate a Program with ID : %s.' % pk)
            return HttpResponseRedirect(reverse('program-detail', kwargs={'pk': pk}))


class DeleteTopic(View):

    def get(self, request, pk):
        topic = Topic.objects.get(pk=pk)
        if Topic.delete(request, pk=pk):
            title = "Deactivate Topic"
            description = f"Topic {topic.name} belonging to Program {topic.program.name} has been deactivated"
            notification_roles = [settings.SOCION_PROGRAM_ADMIN, settings.SOCION_CONTENT_ADMIN, ]
            program_member_admin_ids = list(
                Program_Roles.objects.values_list("user_id", flat=True).filter(role__in=notification_roles,
                                                                               program_id=topic.program.id,
                                                                               deleted=False).distinct())
            if program_member_admin_ids:
                for admin_user_id in program_member_admin_ids:
                    Notifications.notification_save(title=title,
                                                    description=description,
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=None, user_id=admin_user_id, session_id=None)
            program_logger.info('Successfully Deleted a Topic with ID : %s.' % pk)
            return HttpResponseRedirect(reverse('program-detail', kwargs={'pk': topic.program.id}))
        else:
            program_logger.error('Could not Delete a Topic with ID : %s.' % pk)
            return HttpResponseForbidden


class ReactivateTopic(View):

    def get(self, request, pk):
        topic = Topic.objects.get(pk=pk)
        if Topic.reactivate(request, pk=pk):
            title = "Reactivate Topic"
            description = f"Topic {topic.name} belonging to Program {topic.program.name} has been reactivated"
            notification_roles = [settings.SOCION_PROGRAM_ADMIN, settings.SOCION_CONTENT_ADMIN, ]
            program_member_admin_ids = list(
                Program_Roles.objects.values_list("user_id", flat=True).filter(role__in=notification_roles,
                                                                               program_id=topic.program.id,
                                                                               deleted=False).distinct())
            if program_member_admin_ids:
                for admin_user_id in program_member_admin_ids:
                    Notifications.notification_save(title=title,
                                                    description=description,
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=None, user_id=admin_user_id, session_id=None)
            program_logger.info('Successfully Reactivated a Topic with ID : %s.' % pk)
            return HttpResponseRedirect(reverse('program-detail', kwargs={'pk': topic.program.id}))
        else:
            program_logger.error('Could not Reactivate a Topic with ID : %s.' % pk)
            return HttpResponseForbidden


class ProgramMemberDeactivate(View):

    def get(self, request, pk, user_id, role, admin_username):

        if Program_Roles.delete(request, pk=pk, user_id=user_id, role=role):
            program = Program.objects.get(pk=pk)
            admin_ids = list()
            title = ""
            description = ""
            if role == settings.SOCION_PROGRAM_ADMIN:
                title = "Remove Program Admin"
                description = f"Program Administrator access has been withdrawn for {admin_username} from Program {program.name}"
                admin_ids = list(
                    Entity_Role.objects.values_list("user_id", flat=True).filter(role=settings.SOCION_ENTITY_ADMIN,
                                                                                 entity_id=program.entity_id,
                                                                                 deleted=False).distinct())
            elif role == settings.SOCION_CONTENT_ADMIN:
                title = "Remove Content Admin"
                description = f"Content Administrator access has been withdrawn for {admin_username} from Program {program.name}"
            elif role == settings.SOCION_TRAINER:
                title = "Remove Trainer"
                description = f"Trainer, {admin_username}, has been removed from Program {program.name}"
            program_member_admin_ids = list(
                Program_Roles.objects.values_list("user_id", flat=True).filter(role=settings.SOCION_PROGRAM_ADMIN,
                                                                               program_id=pk,
                                                                               deleted=False).distinct())
            program_member_admin_ids.append(user_id)
            net_admin_ids = list(set().union(admin_ids, program_member_admin_ids))
            if net_admin_ids:
                for admin_user_id in net_admin_ids:
                    Notifications.notification_save(title=title,
                                                    description=description,
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=None, user_id=admin_user_id, session_id=None)
            program_logger.info('Successfully Deactivated a Member from Program with ID : %s.' % pk)
            return HttpResponseRedirect(reverse('program-detail', kwargs={'pk': pk}))
        else:
            program_logger.error('Could not Deactivate a Member from Program with ID : %s.' % pk)
            return HttpResponseForbidden


class ProgramMemberReactivate(View):

    def get(self, request, pk, user_id, role, admin_username):

        if Program_Roles.reactivate(request, pk=pk, user_id=user_id, role=role):
            program = Program.objects.get(pk=pk)
            admin_ids = list()
            title = ""
            description = ""
            if role == settings.SOCION_PROGRAM_ADMIN:
                title = "Reactivate Program Admin"
                description = f"Program Administrator, {admin_username}, has been reinstated to Program {program.name}"
                admin_ids = list(
                    Entity_Role.objects.values_list("user_id", flat=True).filter(role=settings.SOCION_ENTITY_ADMIN,
                                                                                 entity_id=program.entity_id,
                                                                                 deleted=False).distinct())
            elif role == settings.SOCION_CONTENT_ADMIN:
                title = "Reactivate Content Admin"
                description = f"Content Administrator, {admin_username}, has been reinstated to Program {program.name}"
            elif role == settings.SOCION_TRAINER:
                title = "Reactivate Trainer"
                description = f"Trainer, {admin_username}, has been reinstated to Program {program.name}"
            program_member_admin_ids = list(
                Program_Roles.objects.values_list("user_id", flat=True).filter(role=settings.SOCION_PROGRAM_ADMIN,
                                                                               program_id=pk,
                                                                               deleted=False).distinct())
            program_member_admin_ids.append(user_id)
            net_admin_ids = list(set().union(admin_ids, program_member_admin_ids))
            if net_admin_ids:
                for admin_user_id in net_admin_ids:
                    Notifications.notification_save(title=title,
                                                    description=description,
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=None, user_id=admin_user_id, session_id=None)
            program_logger.info('Successfully Reactivated a Member from Program with ID : %s.' % pk)
            return HttpResponseRedirect(reverse('program-detail', kwargs={'pk': pk}))
        else:
            program_logger.error('Could not Reactivate a Member from Program with ID : %s.' % pk)
            return HttpResponseForbidden


class CreateTopic(View):

    def get(self, request, pk=None):
        instance = get_object_or_404(Program, pk=pk)
        try:
            form = TopicForm()
            template = 'program/detail/topic_create.html'
            return save_topic(request, form, template, instance)
        except ValueError:
            return False

    def post(self, request, pk):
        instance = get_object_or_404(Program, pk=pk)
        try:
            form = TopicForm(request.POST)
            template = 'program/detail/topic_create.html'
            return save_topic(request, form, template, instance)
        except ValueError:
            return False


def save_topic(request, form, template_name, instance):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            topic = form.save(commit=False)
            topic.program = instance
            topic.save()
            data['topic_id'] = topic.id
            title = "Add Topic"
            description = f"Topic {topic.name} has been added to Program {instance.name}."
            notification_roles = [settings.SOCION_PROGRAM_ADMIN, settings.SOCION_CONTENT_ADMIN, ]
            program_member_admin_ids = list(
                Program_Roles.objects.values_list("user_id", flat=True).filter(role__in=notification_roles,
                                                                               program_id=instance.pk,
                                                                               deleted=False).distinct())
            if program_member_admin_ids:
                for admin_user_id in program_member_admin_ids:
                    Notifications.notification_save(title=title,
                                                    description=description,
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=None, user_id=admin_user_id, session_id=None)
            data['form_is_valid'] = True
            program_logger.info('Successfully Created a Topic to Program %s.' % instance.name)
        else:
            data['form_is_valid'] = False
            program_logger.error('Could not Create a Topic as Form Validation Failed.')
    context = {'form': form, 'program': instance}
    data['html_form'] = render_to_string(template_name, context, request)
    return JsonResponse(data)


class UpdateTopic1(CreateView):
    """
    Edit Topic Details.
    """

    template_name = 'program/detail/topic_update_1.html'
    model = Content
    fields = ['attachment', ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attachment = Content.objects.all()
        context['attachment'] = attachment
        return context

    def get(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk)
        form = TopicUpdateForm1(instance=topic)
        template = 'program/detail/topic_update_1.html'
        return save_topic_update(request, form=form, template_name=template, instance=topic)

    def post(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk)
        try:
            form = TopicUpdateForm1(request.POST, request.FILES, instance=topic)
            template = 'program/detail/topic_update_1.html'
            program = get_object_or_404(Program, pk=topic.program_id)
            if topic.name != request.POST['name'] or topic.description != request.POST['description']:
                title = "Edit Topic."
                description = f"Topic {topic.name} belonging to Program {program.name} has been edited by member {request.user.user_name}."
                notification_roles = [settings.SOCION_PROGRAM_ADMIN, settings.SOCION_CONTENT_ADMIN, ]
                program_member_admin_ids = list(
                    Program_Roles.objects.values_list("user_id", flat=True).filter(role__in=notification_roles,
                                                                                   program_id=program.id,
                                                                                   deleted=False).distinct())
                if program_member_admin_ids:
                    for admin_user_id in program_member_admin_ids:
                        Notifications.notification_save(title=title,
                                                        description=description,
                                                        notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                        date_time=datetime.now(), is_deleted=False, is_read=False,
                                                        role=None, user_id=admin_user_id, session_id=None)
            return save_topic_update(request, form=form, template_name=template, instance=topic)

        except ValueError:
            return HttpResponseRedirect(reverse('program-detail'))


def save_topic_update(request, form, template_name, instance):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            content = form.save(commit=False)
            content.topic = instance
            data['topic_id'] = content.id
            if request.FILES:
                aws_session = boto3.Session(aws_access_key_id=config('AWS_ACCESS_KEY_ID'), aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'))
                s3 = aws_session.resource('s3')
                for file in request.FILES.getlist('inline[]'):
                    if form.cleaned_data.get('topic'):
                        topic_id = form.cleaned_data.get('topic')
                    else:
                        topic_id = instance
                    ext = file.name.split(".")[-1]
                    mimetype = mimetypes.MimeTypes().guess_type(file.name)[0]
                    uuId = uuid.uuid1()
                    if ext in settings.SOCION_VIDEO_FORMAT:
                        v = vimeo.VimeoClient(token=config('VIMEO_ACCESS_TOKEN'))
                        path = file.temporary_file_path()
                        try:
                            # Upload the file and include the video title and description.
                            uri = v.upload(path, data={
                                'name': file.name,
                                'chunk_size': 128 * 1024 * 1024
                                })

                            # Get the metadata response from the upload
                            video_data = v.get(uri + '?fields=link').json()
                            vimeo_url = video_data['link']
                            file_key = "%s%s%s%s" % ("Content Videos/", uuId, ".", ext)
                            s3.Bucket(config('AWS_STORAGE_BUCKET_NAME')).put_object(Key=file_key, Body=file, ContentType=mimetype)
                            url = "%s%s" % (URL, file_key)
                            attachment = Content(topic=topic_id, name=file, created_by=request.user.user_id,
                                                 content_url=url, vimeo_url=vimeo_url, content_type='Video')
                            attachment.save()
                            program_logger.info('Successfully Added a Video to a Topic with ID : %s.' % content.id)

                        except vimeo.exceptions.VideoUploadFailure as e:

                            # print('Error uploading %s' % file.name)
                            # print('Server reported: %s' % e.message)
                            program_logger.error('Could not Add Video to a Topic with ID : %s.' % content.id)
                            pass

                    elif ext in settings.SOCION_IMAGE_FORMAT:
                        file_key = "%s%s%s%s" % ("content/image/", uuId, ".", ext)
                        s3.Bucket(config('AWS_STORAGE_BUCKET_NAME')).put_object(Key=file_key, Body=file, ContentType=mimetype)
                        url = "%s%s" % (URL, file_key)
                        attachment = Content(topic=topic_id, name=file,  content_type='Image',
                                             created_by=request.user.user_id, content_url=url)
                        attachment.save()
                        program_logger.info('Successfully Added an Image to a Topic with ID : %s.' % content.id)
                    elif ext in settings.SOCION_DOC_FORMAT:
                        file_key = "%s%s%s%s" % ("content/document/", uuId, ".", ext)
                        s3.Bucket(config('AWS_STORAGE_BUCKET_NAME')).put_object(Key=file_key, Body=file, ContentType=mimetype)
                        url = "%s%s" % (URL, file_key)
                        attachment = Content(topic=topic_id, name=file, content_type='Document',
                                             created_by=request.user.user_id, content_url=url)
                        attachment.save()
                        program_logger.info('Successfully Added a Document to a Topic with ID : %s.' % content.id)
                program = get_object_or_404(Program, pk=content.program_id)
                title = "Add Content to a Topic."
                description = f"Content has been added to the Topic {content.name} to Program {program.name} by member {request.user.user_name}."
                notification_roles = [settings.SOCION_PROGRAM_ADMIN, settings.SOCION_CONTENT_ADMIN, ]
                program_member_admin_ids = list(
                    Program_Roles.objects.values_list("user_id", flat=True).filter(role__in=notification_roles,
                                                                                   program_id=program.id,
                                                                                   deleted=False).distinct())
                if program_member_admin_ids:
                    for admin_user_id in program_member_admin_ids:
                        Notifications.notification_save(title=title,
                                                        description=description,
                                                        notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                        date_time=datetime.now(), is_deleted=False, is_read=False,
                                                        role=None, user_id=admin_user_id, session_id=None)
            content.save()
            data['form_is_valid'] = True
        else:
            program_logger.error('Could not Add Content to Topic as form validation failed.')
            data['form_is_valid'] = False
    context = {'form': form, 'program': instance}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


class Topic_Update(FormView):
    template_name = 'program/detail/topic_update.html'
    form_class = TopicUpdateForm
    model = Content
    fields = ['attachment', ]

    def get(self, request, pk=None, **kwargs):
        instance = get_object_or_404(Topic, pk=pk)
        form = TopicUpdateForm(instance=instance, initial={'topic': instance.pk})
        return save_topic_update(request, form, 'program/detail/topic_update.html', instance)

    def post(self, request, pk=None, **kwargs):
        if request.method == 'POST':
            instance = get_object_or_404(Topic, pk=pk)
            try:
                form = TopicUpdateForm(request.POST, request.FILES, instance=instance, initial={'topic': instance.pk})
                template = 'program/detail/topic_update.html'
                return save_topic_update(request, form, template, instance)
            except ValueError:
                return False


class Content_Update(FormView):
    template_name = 'program/detail/index.html'
    form_class = ContentForm
    model = Content
    fields = ['attachment', ]

    def get(self, request, pk=None, **kwargs):
        instance = get_object_or_404(Topic, pk=pk)
        form = ContentForm(instance=instance)
        return save_topic_update(request, form, 'program/detail/topic_update.html', instance)

    def post(self, request, pk=None, **kwargs):
        if request.method == 'POST':
            instance = get_object_or_404(Topic, pk=pk)
            try:
                form = ContentForm(request.POST, request.FILES, instance=instance)
                template = 'program/detail/topic_update.html'
                return save_topic_update(request, form, template, instance)
            except ValueError:
                return False


class DeleteContent(View):

    def get(self, request, pk=None):
        content = get_object_or_404(Content, pk=pk)
        content.deletecontent()
        topic = get_object_or_404(Topic, pk=content.topic_id)
        program = get_object_or_404(Program, pk=topic.program_id)
        title = "Delete Content from a Topic."
        description = f"Content has been deleted from the Topic {topic.name} to Program {program.name} by member {request.user.user_name}."
        notification_roles = [settings.SOCION_PROGRAM_ADMIN, settings.SOCION_CONTENT_ADMIN, ]
        program_member_admin_ids = list(
            Program_Roles.objects.values_list("user_id", flat=True).filter(role__in=notification_roles,
                                                                           program_id=program.id,
                                                                           deleted=False).distinct())
        if program_member_admin_ids:
            for admin_user_id in program_member_admin_ids:
                Notifications.notification_save(title=title,
                                                description=description,
                                                notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                date_time=datetime.now(), is_deleted=False, is_read=False,
                                                role=None, user_id=admin_user_id, session_id=None)
        program_logger.info('Deleted Content from a Topic with ID : %s' % topic.id)
        return JsonResponse(data='Removed', safe=False)


class UploadProgramDocument(View):

    def post(self, request, pk):
        program = get_object_or_404(Program, pk=pk)
        program_admin_ids = list(Program_Roles.objects.values_list("user_id", flat=True).filter(program_id=pk, role=settings.SOCION_PROGRAM_ADMIN, deleted=False).distinct())
        entity_admin_ids = list(Entity_Role.objects.values_list("user_id", flat=True).filter(entity_id=program.entity_id, role=settings.SOCION_ENTITY_ADMIN, deleted=False).distinct())
        net_admin_ids = list(set().union(entity_admin_ids, program_admin_ids))
        net_admin_ids.append(program.created_by)
        for file in request.FILES.getlist('inline[]'):
            # print(round(file.size/1000000, 2))
            program_id = program.id
            ext = file.name.split(".")[-1]
            if ext in settings.SOCION_VIDEO_FORMAT:
                v = vimeo.VimeoClient(token=config('VIMEO_ACCESS_TOKEN'))
                path = file.temporary_file_path()
                try:
                    # Upload the file and include the video title and description.
                    uri = v.upload(path, data={
                        'name': file.name,
                        'chunk_size': 128 * 1024 * 1024
                        })

                    # Get the metadata response from the upload and log out the Vimeo.com url
                    video_data = v.get(uri + '?fields=link').json()
                    vimeo_url = video_data['link']
                    file_key = s3_file_upload(request, bucket_name="Program-Docs/Program Videos/")
                    if file_key is not None:
                        url = "%s%s" % (URL, file_key)
                        attachment = ProgramDocument(program_id=program_id, name=file,
                                                     content_url=url, vimeo_url=vimeo_url,
                                                     created_by=request.user.user_id, content_type='Video')
                        attachment.save()
                        program_logger.info('Successfully Added a Video to a Program with ID : %s.' % program_id)

                except vimeo.exceptions.VideoUploadFailure as e:

                    # print('Error uploading %s' % file.name)
                    # print('Server reported: %s' % e.message)
                    program_logger.error('Could not Add Video to a Topic with ID : %s.' % program.id)
                    pass

            elif ext in settings.SOCION_IMAGE_FORMAT:
                file_key = s3_file_upload(request, bucket_name="Program-Docs/Images/")
                if file_key is not None:
                    url = "%s%s" % (URL, file_key)
                    attachment = ProgramDocument(program_id=program_id, name=file, content_url=url,
                                                 created_by=request.user.user_id, content_type='Image')
                    attachment.save()
                    program_logger.info('Successfully Added an Image to a Program with ID : %s.' % program_id)
            elif ext in settings.SOCION_DOC_FORMAT:
                file_key = s3_file_upload(request, bucket_name="Program-Docs/Documents/")
                if file_key is not None:
                    url = "%s%s" % (URL, file_key)
                    attachment = ProgramDocument(program_id=program_id, name=file, content_type='Document',
                                                 created_by=request.user.user_id, content_url=url)
                    attachment.save()
                    program_logger.info('Successfully Added a Document to a Program with ID : %s.' % program_id)
        if net_admin_ids:
            for user_id in net_admin_ids:
                Notifications.notification_save(title='Document Upload.',
                                                description=f"New Document(s) have been uploaded to Program {program.name}.",
                                                notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                date_time=datetime.now(), is_deleted=False, is_read=False,
                                                role=None, user_id=user_id, session_id=None)
        return HttpResponseRedirect(reverse('program-detail', kwargs={'pk': pk}))


class DeleteDocument(View):

    def get(self, request, pk=None):
        document = get_object_or_404(ProgramDocument, pk=pk)
        program_id = document.program_id
        program = get_object_or_404(Program, pk=program_id)
        program_admin_ids = list(Program_Roles.objects.values_list("user_id", flat=True).filter(program_id=program_id, role=settings.SOCION_PROGRAM_ADMIN, deleted=False).distinct())
        entity_admin_ids = list(Entity_Role.objects.values_list("user_id", flat=True).filter(entity_id=program.entity_id, role=settings.SOCION_ENTITY_ADMIN, deleted=False).distinct())
        net_admin_ids = list(set().union(entity_admin_ids, program_admin_ids))
        net_admin_ids.append(program.created_by)
        if ProgramDocument.delete(request, pk=pk):
            if net_admin_ids:
                for user_id in net_admin_ids:
                    Notifications.notification_save(title='Document Delete',
                                                    description=f"Document(s) have been deleted from Program {program.name}.",
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=None, user_id=user_id, session_id=None)
            program_logger.info('Successfully Deleted a Document from a Program with ID : %s.' % program_id)
            return HttpResponseRedirect(reverse('program-detail', kwargs={'pk': program_id}))
        else:
            program_logger.error('Could not Delete a Document from a Program with ID : %s.' % program_id)
            return HttpResponseRedirect(reverse('program-detail', kwargs={'pk': program_id}))


def content_download(request):
    data = dict()
    if request.method == "POST":
        session = boto3.session.Session(region_name=config('AWS_REGION_NAME'))
        s3 = session.client('s3', aws_access_key_id=config('AWS_ACCESS_KEY_ID'), aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'))
        download_url = request.POST['content_url']
        filename = urllib.parse.quote(request.POST['content_name'])
        path = download_url.replace(settings.AWS_STATIC_URL, '')
        try:
            response = s3.generate_presigned_url('get_object',
                                                 Params={'Bucket': config('AWS_STORAGE_BUCKET_NAME'), 'Key': path, 'ResponseContentDisposition': "attachment; filename=%s" % filename},
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

