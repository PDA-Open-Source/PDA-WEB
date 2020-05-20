from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
import json
from core.models import Notification
from socion.info_logs import core_logger


def pop_scanner(template_name, request, **kwargs):
    data = dict()
    if request.method == 'POST':
        data['qr_value'] = kwargs.get('qr_value', None)
        core_logger.info('Scanner Open Successful.')
    data['html_form'] = render_to_string(template_name, request=request)
    return JsonResponse(data)


def scanner(request):
    if request.method == 'POST':
        qr_value = request.POST['QRDecodedString']
        core_logger.info('QR Scan Successful.')
        return pop_scanner('core/scanner.html', request, qr_value=qr_value)
    else:
        core_logger.error('QR Scan Unsuccessful.')
        return pop_scanner('core/scanner.html', request)


def error_page(request):
    return render(request, 'core/error.html')


def inscanner(request):
    if request.method == 'POST':
        core_logger.info('QR Decoding Successful.')
        return redirect('landing')
    else:
        core_logger.error('QR Decoding Unsuccessful.')
        return render(request, 'core/in-body-qrscanner.html')


def pop_notification(template_name, request, **kwargs):
    data = dict()
    if request.method == 'POST':
        notifications = kwargs.get('notification_value', None)
        data['html_notification_list'] = render_to_string('core/partial-notification.html', {'notifications': notifications})
    data['html_form'] = render_to_string(template_name, request=request)
    return JsonResponse(data)


class Contact:

    @staticmethod
    def contact_us(request):
        return render(request, 'core/contact-us.html')


def notification(request):
    if request.method == 'POST':
        notification_value = json.loads(request.POST['notificationObject'])
        return pop_notification('core/notification.html', request, notification_value=notification_value)
    else:
        return pop_notification('core/notification.html', request)


class Notifications:

    @staticmethod
    def notification_save(title, description, notification_type, date_time, is_deleted, is_read, role, user_id, session_id):
        notification_obj = Notification(title=title, description=description, notification_type=notification_type, date_time=date_time, is_deleted=is_deleted, is_read=is_read, role=role, user_id=user_id, session_id=session_id)
        notification_obj.save(using='session_db')

