from datetime import datetime
import requests
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction, connection
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from socion.storage_backends import s3_file_upload
from django.urls import reverse
import vimeo
from django.db.models import Prefetch
from django.views.generic import FormView, DetailView, View, ListView
from django.conf import settings
from apps.entity.forms import EntityForm
from apps.entity.models import Entity, EntityDocument, Entity_Role
from apps.program.models import Program, Program_Roles, Topic
from core.models import Session
from decouple import config
from core.views import Notifications
from socion.info_logs import entity_logger
import uuid
import mimetypes
import boto3
import botocore

URL = settings.AWS_STATIC_URL
cursor = connection.cursor()


def index(request):
    return render(request, 'entity/entity-list.html')


class EntityListView(ListView):
    template_name = "entity/entity-list.html"
    queryset = Entity.objects.filter()
    context_object_name = 'entity'

    def get_queryset(self):
        user_id = self.request.user.user_id
        if settings.SOCION_SUPER_ADMIN in self.request.user.roles:
            return super().get_queryset()
        else:
            entity_admin_ids = Entity_Role.objects.values_list("entity_id").filter(user_id=user_id, deleted=False)
            return super().get_queryset().filter(pk__in=entity_admin_ids)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        un_registered_entities = []
        registered_entities = []
        # List those entities in which User is part of any program
        program_ids = Program_Roles.objects.values_list("program_id", flat=True).filter(user_id=self.request.user.user_id, deleted=False)
        program_admin_ids = Program_Roles.objects.values_list("program_id", flat=True).filter(user_id=self.request.user.user_id, role=settings.SOCION_PROGRAM_ADMIN)
        net_program_ids = set().union(program_ids, program_admin_ids)
        entity_list_ids = Program.objects.values_list("entity_id", flat=True).filter(pk__in=net_program_ids)
        entity = list(Entity.objects.filter(pk__in=entity_list_ids))
        context["object_list"] = set().union(entity, list(context["object_list"]))
        for obj in context["object_list"]:
            entity_user_id = list(Entity_Role.objects.values_list("user_id", flat=True).filter(entity_id=obj.id, deleted=False))
            program_count = len(list(Program.objects.values_list("id", flat=True).filter(entity_id=obj.id)))
            obj.number_of_programs = str(program_count)
            if entity_user_id:
                for userId in entity_user_id:
                    member_info_url = f"{settings.BASE_URL}user/private/details/{userId}"
                    response = requests.get(member_info_url)
                    if response.status_code == 200:
                        data = response.json()
                        obj.admin_user_name = data['name']
                        obj.admin_user_phoneNumber = data['countryCode'] + "-" + data['phoneNumber']
                        entity_logger.info('Fetched details of Entity Admin.')
                        break
            if obj.is_registered:
                registered_entities.append(obj)
            else:
                un_registered_entities.append(obj)
        context["registered_entities"] = registered_entities
        context["un_registered_entities"] = un_registered_entities
        return context


def pop_add_entity(template_name, request, **kwargs):
    data = dict()
    context = None
    qr_value = kwargs.get('qr_value', None)
    if qr_value is not None:
        context = {'qr_value': qr_value}
    if request.method == 'POST':
        created_by = request.user.user_id
        user_id = request.POST.get('socionEntityAdminUser')
        entity_name = request.POST.get('socionEntityName')
        entity = Entity.objects.create(name=entity_name, created_by=created_by)
        Entity_Role.objects.create(entity_id=entity.id, role=settings.SOCION_ENTITY_ADMIN, user_id=user_id, created_at=datetime.now(),
                                   updated_at=datetime.now(), deleted=bool(False), created_by=created_by)
        Notifications.notification_save(title='Invite Entity',
                                        description=f"Entity {entity_name} has been invited to register.",
                                        notification_type=settings.NOTIFICATION_TYPE["USER"],
                                        date_time=datetime.now(), is_deleted=False, is_read=False,
                                        role=settings.SOCION_SUPER_ADMIN, user_id=created_by, session_id=None)
        Notifications.notification_save(title='Receive Invitation',
                                        description=f"Congratulations! You have been invited to register your entity. Please complete the registration process.",
                                        notification_type=settings.NOTIFICATION_TYPE["USER"],
                                        date_time=datetime.now(), is_deleted=False, is_read=False,
                                        role=settings.SOCION_ENTITY_ADMIN, user_id=user_id, session_id=None)
        data['form_is_valid'] = True
        entity_logger.info('Successfully Invited an Entity %s.' % entity_name)
    else:
        entity_logger.error('Could not Invite an Entity')
    data['html_form'] = render_to_string(template_name, context=context, request=request)
    return JsonResponse(data)


def add_entity(request):
    return pop_add_entity('entity/add-entity.html', request)


def choose_scan_type(request):
    return pop_add_entity('entity/choose-scan-type.html', request)


def add_entity_info(request, qr_value):
    if request.method == 'POST':
        return pop_add_entity('entity/add-entity-info.html', request, qr_value=qr_value)
    else:
        return pop_add_entity('entity/add-entity-info.html', request, qr_value=qr_value)


def pop_add_entity_admin(template_name, request, **kwargs):
    data = dict()
    context = None
    qr_value = kwargs.get('qr_value', None)
    if qr_value is not None:
        context = {'qr_value': qr_value}
    if request.method == 'POST':
        user_id = request.POST.get('userId')
        role = request.POST.get('entityRole')
        entity_id = request.POST.get('entityId')
        member_name = request.POST.get('entityName')
        entity = get_object_or_404(Entity, pk=entity_id)
        entity_admin_ids = list(Entity_Role.objects.values_list("user_id", flat=True).filter(role=settings.SOCION_ENTITY_ADMIN, entity_id=entity_id, deleted=False).distinct())
        query = '''INSERT INTO Entity_Role (entity_id, role, user_id, created_at, updated_at, created_by, deleted) VALUES (%s,%s,%s,%s,%s,%s,%s)'''
        try:
            query_data = (entity_id, role, user_id, datetime.now(), datetime.now(), request.user.user_id, False)
            cursor.execute(query, query_data)
            transaction.commit()
            for entity_admin_id in entity_admin_ids:
                Notifications.notification_save(title='Add Entity Admin.',
                                                description=f"{member_name} has onboarded as Entity Admin to entity {entity.name}.",
                                                notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                date_time=datetime.now(), is_deleted=False, is_read=False,
                                                role=settings.SOCION_ENTITY_ADMIN, user_id=entity_admin_id, session_id=None)
            Notifications.notification_save(title='Add Entity Admin.',
                                            description=f"{member_name} has onboarded as Entity Admin to entity {entity.name}.",
                                            notification_type=settings.NOTIFICATION_TYPE["USER"],
                                            date_time=datetime.now(), is_deleted=False, is_read=False,
                                            role=settings.SOCION_SUPER_ADMIN, user_id=entity.created_by, session_id=None)
            Notifications.notification_save(title='Add Entity Admin.',
                                            description=f"You have been onboarded as Entity admin to entity {entity.name}.",
                                            notification_type=settings.NOTIFICATION_TYPE["USER"],
                                            date_time=datetime.now(), is_deleted=False, is_read=False,
                                            role=settings.SOCION_ENTITY_ADMIN, user_id=user_id, session_id=None)
            data['form_is_valid'] = True
            entity_logger.info('Successfully Added an Entity Admin to Entity with ID : %s.' % entity_id)
        except (Exception, ValueError):
            data['form_is_valid'] = False
            entity_logger.error('Could not Add an Entity Admin.')
    else:
        entity_logger.error('Could not Add an Entity Admin as the Method was not allowed.')
        data['form_is_valid'] = False

    data['html_form'] = render_to_string(template_name, context=context, request=request)
    return JsonResponse(data)


def add_entity_admin(request):
    return pop_add_entity_admin('entity/add-entity-admin.html', request)


def add_entity_admin_info(request, qr_value):
    if request.method == 'POST':
        return pop_add_entity_admin('entity/add-entity-admin-info.html', request, qr_value=qr_value)
    else:
        return pop_add_entity_admin('entity/add-entity-admin-info.html', request, qr_value=qr_value)


class RegisterEntity(FormView):
    """
    Form to Register Entity Details.
    """

    def get(self, request, pk):
        data = dict()
        entity = get_object_or_404(Entity, pk=pk)
        entity_user_id = list(Entity_Role.objects.values_list("user_id", flat=True).filter(entity_id=entity.id))
        if entity_user_id:
            userId = entity_user_id[0]
            member_info_url = f"{settings.BASE_URL}user/private/details/{userId}"
            response = requests.get(member_info_url)
            if response.status_code == 200:
                data = response.json()
                data['entity_name'] = entity.name
                entity_logger.info('Fetched details of Entity Admin for Entity %s.' % entity.name)
        form = EntityForm(instance=entity)
        template = 'entity/register-entity.html'
        return save_all(request, form=form, template_name=template, content=data)

    def post(self, request, pk):
        entity = get_object_or_404(Entity, pk=pk)
        entity_user_id = list(Entity_Role.objects.values_list("user_id", flat=True).filter(entity_id=entity.id))

        try:
            form = EntityForm(request.POST, request.FILES, instance=entity)
            template = 'entity/register-entity.html'
            if request.FILES:
                aws_session = boto3.Session(aws_access_key_id=config('AWS_ACCESS_KEY_ID'), aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'))
                s3 = aws_session.resource('s3')
                for file in request.FILES.getlist('inline[]'):
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
                            file_key = "%s%s%s%s" % ("entity-docs/Entity Videos/", uuId, ".", ext)
                            s3.Bucket(config('AWS_STORAGE_BUCKET_NAME')).put_object(Key=file_key, Body=file, ContentType=mimetype)
                            url = "%s%s" % (URL, file_key)
                            attachment = EntityDocument(entity=entity, name=file, content_url=url, vimeo_url=vimeo_url,
                                                        created_by=request.user.user_id, content_type='Video')
                            attachment.save()
                            entity_logger.info('Successfully Added a Video to an Entity with ID : %s.' % entity.id)
                        except vimeo.exceptions.VideoUploadFailure or botocore.exceptions.ClientError as e:
                            # We may have had an error. We can't resolve it here necessarily, so
                            # report it to the user.
                            # print('Error uploading %s' % file.name)
                            # print('Server reported: %s' % e.message)
                            entity_logger.error('Could not Add Video to an Entity with ID : %s.' % entity.id)
                            pass

                    elif ext in settings.SOCION_IMAGE_FORMAT:
                        file_key = "%s%s%s%s" % ("entity-docs/image/", uuId, ".", ext)
                        s3.Bucket(config('AWS_STORAGE_BUCKET_NAME')).put_object(Key=file_key, Body=file, ContentType=mimetype)
                        url = "%s%s" % (URL, file_key)
                        attachment = EntityDocument(entity=entity, name=file, content_type='Image',
                                                    created_by=request.user.user_id, content_url=url)
                        attachment.save()
                        entity_logger.info('Successfully Added an Image to an Entity with ID : %s.' % entity.id)

                    elif ext in settings.SOCION_DOC_FORMAT:
                        file_key = "%s%s%s%s" % ("entity-docs/document/", uuId, ".", ext)
                        s3.Bucket(config('AWS_STORAGE_BUCKET_NAME')).put_object(Key=file_key, Body=file, ContentType=mimetype)
                        url = "%s%s" % (URL, file_key)
                        attachment = EntityDocument(name=file, entity=entity, content_url=url,
                                                    created_by=request.user.user_id, content_type='Document')
                        attachment.save()
                        entity_logger.info('Successfully Added a Document to an Entity with ID : %s.' % entity.id)

                if entity_user_id:
                    userId = entity_user_id[0]
                    Notifications.notification_save(title='Entity upload document.',
                                                    description=f"Document(s) have been uploaded to entity {entity.name} profile.",
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=settings.SOCION_SUPER_ADMIN, user_id=entity.created_by, session_id=None)
                    Notifications.notification_save(title='Entity upload document.',
                                                    description=f"Document(s) have been uploaded to entity {entity.name} profile.",
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=settings.SOCION_ENTITY_ADMIN, user_id=userId, session_id=None)
            if form.is_valid():
                if entity_user_id:
                    userId = entity_user_id[0]
                    Notifications.notification_save(title='Invite Entity',
                                                    description=f"Entity {entity.name} has been registered.",
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=settings.SOCION_SUPER_ADMIN, user_id=entity.created_by, session_id=None)
                    Notifications.notification_save(title='Invite Entity',
                                                    description=f"Entity {entity.name} has been registered.",
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=settings.SOCION_ENTITY_ADMIN, user_id=userId, session_id=None)
                    entity.register()
                entity_logger.info('Successfully Registered an Entity with ID : %s.' % entity.id)
            return save_all(request, form=form, template_name=template)
        except ValueError:
            entity_logger.error('Could not Register an Entity with ID : %s.' % entity.id)
            return HttpResponseRedirect(reverse('entities'))


def count_of_values_changed(old_object, new_object):
    count = 0
    if old_object.name != new_object['name']:
        count = count + 1
    if old_object.business_registration_number != new_object['business_registration_number']:
        count = count + 1
    if old_object.tax_registration_number != new_object['tax_registration_number']:
        count = count + 1
    if old_object.address_line1 != new_object['address_line1']:
        count = count + 1
    if old_object.address_line2 != new_object['address_line2']:
        count = count + 1
    return count


class EditEntityProfile(FormView):
    """
    Form to Edit Entity Details.
    """

    def get(self, request, pk):
        entity = get_object_or_404(Entity, pk=pk)
        form = EntityForm(instance=entity)
        template = 'entity/edit_entity_profile.html'
        return save_all(request, form=form, template_name=template)

    def post(self, request, pk):
        entity = get_object_or_404(Entity, pk=pk)
        form = EntityForm(request.POST, instance=entity)
        template = 'entity/edit_entity_profile.html'
        description = f"Entity details of {entity.name} has been changed."
        title = "Edit Entity Details."
        if form.is_valid():
            if count_of_values_changed(get_object_or_404(Entity, pk=pk), request.POST) > 1:
                title = "Edit Entity Details."
                description = f"Entity details of {entity.name} has been changed."
            elif get_object_or_404(Entity, pk=pk).name != request.POST['name']:
                title = f"Edit Entity Name."
                description = f"Entity {get_object_or_404(Entity, pk=pk).name} name has been updated to {request.POST['name']}."
            elif get_object_or_404(Entity, pk=pk).business_registration_number != request.POST['business_registration_number']:
                title = f"Edit Entity Registration Number."
                description = f"Entity {get_object_or_404(Entity, pk=pk).name} Business Registration Number has been updated."
            elif get_object_or_404(Entity, pk=pk).tax_registration_number != request.POST['tax_registration_number']:
                title = f"Edit Entity Tax Registration Number."
                description = f"Entity {get_object_or_404(Entity, pk=pk).name} Tax Registration Number has been updated."
            elif get_object_or_404(Entity, pk=pk).address_line1 != request.POST['address_line1']:
                title = f"Edit Entity Address."
                description = f"Entity {get_object_or_404(Entity, pk=pk).name} Address has been updated."
            elif get_object_or_404(Entity, pk=pk).address_line2 != request.POST['address_line2']:
                title = f"Edit Entity Address."
                description = f"Entity {get_object_or_404(Entity, pk=pk).name} Address has been updated."
            entity_admin_ids = list(Entity_Role.objects.values_list("user_id", flat=True).filter(role=settings.SOCION_ENTITY_ADMIN, entity_id=pk, deleted=False).distinct())
            if count_of_values_changed(get_object_or_404(Entity, pk=pk), request.POST) != 0:
                for entity_admin_id in entity_admin_ids:
                    Notifications.notification_save(title=title,
                                                    description=description,
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=settings.SOCION_ENTITY_ADMIN, user_id=entity_admin_id, session_id=None)
                Notifications.notification_save(title=title,
                                                description=description,
                                                notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                date_time=datetime.now(), is_deleted=False, is_read=False,
                                                role=settings.SOCION_SUPER_ADMIN, user_id=entity.created_by, session_id=None)
        return save_all(request, form=form, template_name=template)


def save_all(request, form, template_name, content=None):
    data = dict()
    if request.method == 'POST' or 'GET':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            entity_logger.info('Successfully Edited an Entity with ID : %s.' % form.instance.id)
        else:
            data['form_is_valid'] = False
        context = {'form': form, 'data': content}
        data['html_form'] = render_to_string(template_name, context, request=request)
        return JsonResponse(data)
    else:
        entity_logger.error('Could not Edit an Entity with Id : %s.' % form.instance.id)
        return False


class EntityMixin(UserPassesTestMixin):

    def test_func(self):
        if not self.request.is_logged_in:
            return None

        user_id = self.request.user.user_id
        pk = self.kwargs[self.pk_url_kwarg]
        entity_role = list(
            Entity_Role.objects.values_list("role", flat=True).filter(user_id=user_id, entity_id=pk, deleted=False).distinct()
        )
        program_ids = Program.objects.values_list("id", flat=True).filter(entity_id=pk)
        socion_roles = list(
            Program_Roles.objects.values_list("role", flat=True).filter(user_id=user_id, program_id__in=program_ids, deleted=False).distinct()
        )
        entity_role.extend(socion_roles)
        if settings.SOCION_SUPER_ADMIN not in self.request.user.roles:
            if entity_role:
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


def get_programs(entity_id, **kwargs):
    program_ids = kwargs.get('program_ids', None)
    if program_ids:
        programs = Program.objects.filter(pk__in=program_ids, entity=entity_id).prefetch_related('documents')
    else:
        programs = Program.objects.filter(entity=entity_id).prefetch_related('documents')
    if programs:
        for program in programs:
            session_ids = Session.objects.using('session_db').values_list("id", flat=True).filter(program_id=program.id, is_deleted=False)
            program.session = len(session_ids)
    return programs


class EntityProfile(EntityMixin, DetailView):
    """
    Profile View of Entity.
    """

    model = Entity
    template_name = 'entity/entity_profile.html'
    context_object_name = 'entity'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        entity_admin = list()
        user_id = self.request.user.user_id
        pk = self.kwargs.get(self.pk_url_kwarg)
        context = super().get_context_data(**kwargs)
        context["contents"] = Entity.objects.filter(deleted=False, id=pk).prefetch_related(Prefetch(
                                                                    'entity_documents',
                                                                    queryset=EntityDocument.objects.filter(deleted=False)))
        admin_list_url = f"{settings.BASE_URL}entity/role/{pk}"
        response = requests.get(admin_list_url)
        if response.status_code == 200:
            entity_admin = response.json()
            entity_logger.info('Successfully Fetched Members for an Entity with ID : %s.' % pk)
        context['ENTITY_ADMIN'] = sorted(entity_admin, key=lambda i: i['deactivated'])
        context["ENTITY_ADMIN_ACTIVE"] = sum(admin['deactivated'] == False for admin in entity_admin)
        context['ENTITY_ADMIN_ACTIVE_COUNT'] = len(list(filter(lambda i: i['deactivated'] is False, entity_admin)))
        if settings.SOCION_SUPER_ADMIN in self.request.user.roles:
            context["programs"] = get_programs(pk)
        else:
            entity_id = list(Entity_Role.objects.values_list("entity_id", flat=True).filter(entity_id=pk, user_id=self.request.user.user_id, deleted=False))
            if entity_id:
                context["programs"] = get_programs(pk)
            else:
                program_ids = list(Program_Roles.objects.values_list("program_id", flat=True).filter(user_id=self.request.user.user_id, deleted=False))
                context["programs"] = get_programs(pk, program_ids=program_ids)
        entity_role = list(
            Entity_Role.objects.values_list("role", flat=True).filter(user_id=user_id, entity_id=pk,
                                                                      deleted=False).distinct()
        )
        if settings.SOCION_SUPER_ADMIN not in self.request.user.roles:
            if settings.SOCION_ENTITY_ADMIN in entity_role:
                context["entity_permissions"] = settings.ENTITY_PERMISSIONS
        return context


class DeactivateEntity(View):
    """
    Deactivation of Entity.
    """

    def get(self, request, pk=None):

        if Entity.delete(request, pk=pk):
            entity = Entity.objects.get(pk=pk)
            entity_admin_ids = list(
                Entity_Role.objects.values_list("user_id", flat=True).filter(entity_id=pk,
                                                                             deleted=False).distinct())
            programs = Program.objects.filter(entity_id=pk)
            programs_ids = Program.objects.values_list("id", flat=True).filter(entity_id=pk)
            topics = Topic.objects.filter(program_id__in=programs_ids)
            roles = Program_Roles.objects.values_list("role", flat=True).filter(program_id__in=programs_ids)
            programs.update(deleted=True)
            topics.update(deleted=True)
            roles.update(deleted=True)
            if entity_admin_ids:
                for admin_user_id in entity_admin_ids:
                    Notifications.notification_save(title="Deactivate Entity",
                                                    description=f"Entity {entity.name} has been deactivated by {request.user.username}",
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=None, user_id=admin_user_id, session_id=None)
            entity_logger.info('Successfully Deactivated an Entity with ID : %s.' % entity.id)
            return HttpResponseRedirect(reverse('index'))
        else:
            entity_logger.error('Could not Deactivate an Entity with ID : %s.' % pk)
            return HttpResponseRedirect(reverse('entity_profile', kwargs={'pk': pk}))


class ReactivateEntity(View):

    def get(self, request, pk=None):
        entity = get_object_or_404(Entity, pk=pk)
        entity_admin_ids = list(Entity_Role.objects.values_list("user_id", flat=True).filter(role=settings.SOCION_ENTITY_ADMIN, entity_id=pk, deleted=False).distinct())
        user_detail_url = f"{settings.BASE_URL}user/private/details/{request.user.user_id}"
        response = requests.get(user_detail_url)
        if response.status_code == 200:
            member = response.json()
            member_name = member['name']
            entity_logger.info('Successfully Fetched Details of member from an Entity with ID : %s.' % entity.id)
        if Entity.reactivate(request, pk=pk):
            for entity_admin_id in entity_admin_ids:
                Notifications.notification_save(title='Remove Entity Admin.',
                                                description=f"Entity {entity.name} has been reactivated by {member_name}.",
                                                notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                date_time=datetime.now(), is_deleted=False, is_read=False,
                                                role=settings.SOCION_ENTITY_ADMIN, user_id=entity_admin_id, session_id=None)
            Notifications.notification_save(title='Remove Entity Admin.',
                                            description=f"Entity {entity.name} has been reactivated by {member_name}.",
                                            notification_type=settings.NOTIFICATION_TYPE["USER"],
                                            date_time=datetime.now(), is_deleted=False, is_read=False,
                                            role=settings.SOCION_SUPER_ADMIN, user_id=entity.created_by, session_id=None)
            entity_logger.info('Successfully Reactivated an Entity with ID : %s.' % entity.id)
            return HttpResponseRedirect(reverse('index'))
        else:
            entity_logger.error('Could not Reactivate an Entity with ID : %s.' % entity.id)
            return HttpResponseRedirect(reverse('entity_profile', kwargs={'pk': pk}))


class DeactivateEntityAdmin(View):

    def get(self, request, pk, user_id, member_name):

        if Entity_Role.delete(request, pk=pk, user_id=user_id):

            entity = get_object_or_404(Entity, pk=pk)
            entity_admin_ids = list(Entity_Role.objects.values_list("user_id", flat=True).filter(role=settings.SOCION_ENTITY_ADMIN, entity_id=pk, deleted=False).distinct())
            admin_user_ids = [user_id, entity.created_by, ]
            net_admin_ids = list(set().union(entity_admin_ids, admin_user_ids))
            if net_admin_ids:
                title = 'Remove Entity Admin.'
                for entity_admin_id in net_admin_ids:
                    if entity_admin_id == user_id:
                        description = f"You have been withdrawn as Entity admin to entity {entity.name}."
                    else:
                        description = f"{member_name} has been withdrawn as Entity admin to entity {entity.name}."
                    Notifications.notification_save(title=title,
                                                    description=description,
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=settings.SOCION_ENTITY_ADMIN, user_id=entity_admin_id, session_id=None)
            entity_logger.info('Successfully Deactivated an Entity Admin from an Entity with ID : %s.' % entity.id)
            return HttpResponseRedirect(reverse('entity-profile', kwargs={'pk': pk}))
        else:
            entity_logger.error('Could not Deactivate an Entity Admin from an Entity with ID : %s.' % pk)
            return HttpResponseForbidden


class ReactivateEntityAdmin(View):

    def get(self, request, pk, user_id, admin_username):

        if Entity_Role.reactivate(request, pk=pk, user_id=user_id):
            entity = Entity.objects.get(pk=pk)
            entity_admin_ids = list(Entity_Role.objects.values_list("user_id", flat=True).filter(entity_id=pk, deleted=False).distinct())
            admin_user_ids = [user_id, entity.created_by, ]
            net_admin_ids = list(set().union(entity_admin_ids, admin_user_ids))
            if net_admin_ids:
                title = "Reactivate Entity Admin"
                description = f"Entity Administrator, {admin_username}, has been reinstated to Entity {entity.name}"
                for admin_user_id in net_admin_ids:
                    Notifications.notification_save(title=title,
                                                    description=description,
                                                    notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                    date_time=datetime.now(), is_deleted=False, is_read=False,
                                                    role=None, user_id=admin_user_id, session_id=None)
            entity_logger.info('Successfully Reactivated an Entity Admin from an Entity with ID : %s.' % entity.id)
            return HttpResponseRedirect(reverse('entity-profile', kwargs={'pk': pk}))
        else:
            entity_logger.error('Could not Reactivate an Entity Admin from an Entity with ID : %s.' % pk)
            return HttpResponseForbidden


class UploadEntityDocument(View):

    def post(self, request, pk):

        entity = get_object_or_404(Entity, pk=pk)
        entity_admin_ids = list(Entity_Role.objects.values_list("user_id", flat=True).filter(role=settings.SOCION_ENTITY_ADMIN, entity_id=pk, deleted=False).distinct())
        for file in request.FILES.getlist('inline[]'):
            print(file.size)
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
                    file_key = s3_file_upload(request, bucket_name="entity-docs/Entity Videos/")
                    if file_key is not None:
                        url = "%s%s" % (URL, file_key)
                        attachment = EntityDocument(entity=entity, name=file, content_url=url, vimeo_url=vimeo_url,
                                                    created_by=request.user.user_id, content_type='Video')
                        attachment.save()
                        entity_logger.info('Successfully Added a Video to an Entity with ID : %s.' % entity.id)
                except vimeo.exceptions.VideoUploadFailure as e:
                    # We may have had an error. We can't resolve it here necessarily, so
                    # report it to the user.
                    # print('Error uploading %s' % file.name)
                    # print('Server reported: %s' % e.message)
                    entity_logger.error('Could not Add Video to an Entity with ID : %s.' % entity.id)
                    pass

            elif ext in settings.SOCION_IMAGE_FORMAT:
                file_key = s3_file_upload(request, bucket_name="entity-docs/image/")
                if file_key is not None:
                    url = "%s%s" % (URL, file_key)
                    attachment = EntityDocument(entity=entity, name=file, content_type='Image',
                                                created_by=request.user.user_id, content_url=url)
                    attachment.save()
                    entity_logger.info('Successfully Added an Image to an Entity with ID : %s.' % entity.id)
            elif ext in settings.SOCION_DOC_FORMAT:
                file_key = s3_file_upload(request, bucket_name="entity-docs/document/")
                if file_key is not None:
                    url = "%s%s" % (URL, file_key)
                    attachment = EntityDocument(name=file, entity=entity, content_url=url,
                                                created_by=request.user.user_id, content_type='Document')
                    attachment.save()
                    entity_logger.info('Successfully Added a Document to an Entity with ID : %s.' % entity.id)

        for entity_admin_id in entity_admin_ids:
            Notifications.notification_save(title='Entity upload document.',
                                            description=f"Document(s) have been uploaded to entity {entity.name} profile.",
                                            notification_type=settings.NOTIFICATION_TYPE["USER"],
                                            date_time=datetime.now(), is_deleted=False, is_read=False,
                                            role=settings.SOCION_ENTITY_ADMIN, user_id=entity_admin_id, session_id=None)
        Notifications.notification_save(title='Entity upload document.',
                                        description=f"Document(s) have been uploaded to entity {entity.name} profile.",
                                        notification_type=settings.NOTIFICATION_TYPE["USER"],
                                        date_time=datetime.now(), is_deleted=False, is_read=False,
                                        role=settings.SOCION_SUPER_ADMIN, user_id=entity.created_by, session_id=None)
        return HttpResponseRedirect(reverse('entity-profile', kwargs={'pk': pk}))


class DeleteDocument(View):

    def get(self, request, pk=None):
        document = get_object_or_404(EntityDocument, pk=pk)
        entity_id = document.entity_id
        entity = get_object_or_404(Entity, pk=entity_id)
        entity_admin_ids = list(Entity_Role.objects.values_list("user_id", flat=True).filter(role=settings.SOCION_ENTITY_ADMIN, entity_id=entity_id, deleted=False).distinct())
        if EntityDocument.delete(request, pk=pk):
            for entity_admin_id in entity_admin_ids:
                Notifications.notification_save(title='Entity delete document.',
                                                description=f"Document(s) have been deleted from entity {entity.name} profile.",
                                                notification_type=settings.NOTIFICATION_TYPE["USER"],
                                                date_time=datetime.now(), is_deleted=False, is_read=False,
                                                role=settings.SOCION_ENTITY_ADMIN, user_id=entity_admin_id, session_id=None)
            entity_logger.info('Successfully Deleted a Document from an Entity with ID : %s.' % entity.id)
            return HttpResponseRedirect(reverse('entity-profile', kwargs={'pk': entity_id}))
        else:
            entity_logger.info('Could not Delete a Document from an Entity with ID : %s.' % entity.id)
            return HttpResponseRedirect(reverse('entity-profile', kwargs={'pk': entity_id}))
