import base64
from django.shortcuts import redirect
from socion import settings


class SocionUserMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        response = self.get_response(request)
        return response

    @staticmethod
    def process_view(request, view_func, view_args, view_kwargs):
        socion_userid_key = base64.b64encode(bytes('socion_userid', 'utf-8')).decode("utf-8").replace("==", "")
        socion_username_key = base64.b64encode(bytes('socion_username', "utf-8")).decode("utf-8").replace("==", "")
        socion_userroles_key = base64.b64encode(bytes('socion_userroles', "utf-8")).decode("utf-8").replace("==", "")

        urls_not_required_auth = ['login', 'signup-request-otp', 'signup-create-password', 'forgot-password',
                                  'reset-password', 'terms-and-conditions', 'privacy-policy', 'attestation-detail',
                                  'contact-us', ]
        if request.resolver_match.url_name in urls_not_required_auth:
            return
        try:
            socion_userid_value = request.COOKIES[socion_userid_key]
            socion_username_value = request.COOKIES[socion_username_key]
            socion_userroles_value = request.COOKIES[socion_userroles_key]
            socion_user_name_value = request.COOKIES['active_user']
            user_id = base64.b64decode(socion_userid_value).decode("utf-8")
            user_name = base64.b64decode(socion_username_value).decode("utf-8")
            user_role = base64.b64decode(socion_userroles_value).decode("utf-8")
            request.is_logged_in = True
            request.user.username = user_name
            request.user.user_id = user_id
            request.user.user_name = socion_user_name_value
            socion_roles = []
            if user_role == 'admin':
                socion_roles.append(settings.SOCION_SUPER_ADMIN)
            # else:
                # query to program table
                # socion_roles = list(
                #     Program_Roles.objects.values_list("role", flat=True).filter(user_id=user_id).distinct()
                # )
                #
                # # query to entity table
                # entity_socion_roles = list(
                #     Entity_Role.objects.values_list("role", flat=True).filter(user_id=user_id).distinct()
                # )
                # socion_roles.extend(entity_socion_roles)

            request.user.roles = socion_roles

        except KeyError:
            # current_page_url = request.path_info.lstrip('/')
            # page_url = request.path.startswith('/oauth/')
            # ignore_url_list = settings.IGNORE_URL_LIST
            # if current_page_url in ignore_url_list or page_url:
            #     return None
            # else:
            request.is_logged_in = False
            response = redirect(settings.LOGIN_URL)
            for cookie in request.COOKIES:
                response.delete_cookie(cookie)
            return response
