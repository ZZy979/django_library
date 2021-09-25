from django.contrib.auth.mixins import UserPassesTestMixin


class LoginAsReaderRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_reader()


class LoginAsLibrarianRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_librarian()
