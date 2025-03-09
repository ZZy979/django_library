from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User, Category


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class UserProfileForm(UserChangeForm):
    password = None

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'email']


class BookSearchForm(forms.Form):
    title = forms.CharField(max_length=200, required=False)
    author = forms.CharField(max_length=100, required=False)
    isbn = forms.CharField(max_length=13, required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)


class BorrowRecordSearchForm(forms.Form):
    username = forms.CharField(max_length=150, required=False)
    isbn = forms.CharField(max_length=13, required=False)
