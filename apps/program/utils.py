class CookieUserMixin:
    def get_login_user_id(self):
        if self.is_user_logged_in:
            return self.get_user_id()

    @property
    def is_user_logged_in(self):
        """
        function which checks user logged in or not
        """
        try:
            return bool(self.request.COOKIES['socion_user_id'])
        except KeyError:
            return False

    def get_user_id(self):
        """
        function which return login user id
        """
        return self.request.COOKIES.get('socion_user_id', 1)


