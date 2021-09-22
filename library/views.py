import re

from django.conf import settings
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.base import View

from .models import User, Reader, Book


class LoginView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('library:index')
        return render(request, 'library/account/login.html', {'login_url': request.get_full_path()})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.can_login():
            login(request, user)
            return redirect(self.get_redirect_url())
        else:
            return render(request, 'library/account/login.html', {'message': '用户名或密码错误'})

    def get_redirect_url(self):
        return self.request.POST.get(REDIRECT_FIELD_NAME) \
               or self.request.GET.get(REDIRECT_FIELD_NAME, 'library:index')


def logout_view(request):
    logout(request)
    return redirect('library:login')


class RegisterView(View):

    def get(self, request):
        return render(request, 'library/account/register.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = ''

        if not re.fullmatch('[0-9A-Za-z_]+', username):
            message = '用户名只能包含字母、数字和下划线'
        elif User.objects.filter(username=username).exists():
            message = '用户名已存在'
        elif password != password2:
            message = '两次密码不一致'

        if message:
            return render(request, 'library/account/register.html', {'message': message})
        user = User.objects.create_user(username, email, password, first_name=name)
        user.groups.add(Group.objects.get(name=settings.READER_GROUP))
        Reader.objects.create(user=user)
        return redirect('library:login')


@login_required
def index(request):
    if request.user.is_librarian():
        return render(request, 'library/librarian/index.html')
    else:
        return render(request, 'library/reader/index.html')


@user_passes_test(User.is_reader)
@login_required
def search(request):
    return render(request, 'library/reader/search.html')


class SearchBookView(UserPassesTestMixin, ListView):
    template_name = 'library/reader/book_list.html'

    def get_queryset(self):
        return Book.objects.filter(title__contains=self.request.GET['title'])

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_reader()


class BookDetailView(UserPassesTestMixin, DetailView):
    model = Book
    template_name = 'library/reader/book_detail.html'

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_reader()
