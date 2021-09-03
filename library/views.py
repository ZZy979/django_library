import re

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.base import View

from .models import User, Reader, Book


def index(request):
    return render(request, 'library/index.html')


class LoginView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('library:index')
        return render(request, 'library/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.can_login():
            login(request, user)
            return redirect('library:index')
        else:
            return render(request, 'library/login.html', {'message': '用户名或密码错误'})


def logout_view(request):
    logout(request)
    return redirect('library:index')


class RegisterView(View):

    def get(self, request):
        return render(request, 'library/register.html')

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
            return render(request, 'library/register.html', {'message': message})
        user = User.objects.create_user(username, email, password, first_name=name)
        user.groups.add(Group.objects.get(name=settings.READER_GROUP))
        Reader.objects.create(user=user)
        return redirect('library:index')


def search(request):
    return render(request, 'library/search.html')


class SearchBookView(ListView):

    def get_queryset(self):
        return Book.objects.filter(title__contains=self.request.GET['title'])


class BookDetailView(DetailView):
    model = Book
