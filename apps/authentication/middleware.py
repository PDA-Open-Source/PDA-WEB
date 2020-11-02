import base64
from django.shortcuts import redirect
from pda import settings


class PdaUserMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        response = self.get_response(request)
        return response

    @staticmethod
    def process_view(request, view_func, view_args, view_kwargs):
        pda_userid_key = base64.b64encode(bytes('pda_userid', 'utf-8')).decode("utf-8").replace("==", "")
        pda_username_key = base64.b64encode(bytes('pda_username', "utf-8")).decode("utf-8").replace("==", "")
        pda_userroles_key = base64.b64encode(bytes('pda_userroles', "utf-8")).decode("utf-8").replace("==", "")

        urls_not_required_auth = ['login', 'signup-request-otp', 'signup-create-password', 'forgot-password',
                                  'reset-password', 'terms-and-conditions', 'privacy-policy', 'attestation-detail',
                                  'contact-us', ]
        if request.resolver_match.url_name in urls_not_required_auth:
            return
        try:
            pda_userid_value = request.COOKIES[pda_userid_key]
            pda_username_value = request.COOKIES[pda_username_key]
            pda_userroles_value = request.COOKIES[pda_userroles_key]
            pda_user_name_value = request.COOKIES['active_user']
            user_id = base64.b64decode(pda_userid_value).decode("utf-8")
            user_name = base64.b64decode(pda_username_value).decode("utf-8")
            user_role = base64.b64decode(pda_userroles_value).decode("utf-8")
            request.is_logged_in = True
            request.user.username = user_name
            request.user.user_id = user_id
            request.user.user_name = pda_user_name_value
            pda_roles = []
            if user_role == 'admin':
                pda_roles.append(settings.PDA_SUPER_ADMIN)

            request.user.roles = pda_roles

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
