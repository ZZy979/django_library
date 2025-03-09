from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin

from .forms import UserRegisterForm, BookSearchForm, UserProfileForm, BorrowRecordSearchForm
from .models import Book, BorrowRecord


def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('library:login')
    else:
        form = UserRegisterForm()
    return render(request, 'library/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('library:book-list')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'library/login.html')


def user_logout(request):
    logout(request)
    return redirect('library:login')


class UserProfileView(LoginRequiredMixin, UpdateView):
    form_class = UserProfileForm
    template_name = 'library/user_profile.html'
    success_url = reverse_lazy('library:book-list')

    def get_object(self, queryset=None):
        return self.request.user


class SearchBookView(FormMixin, ListView):
    form_class = BookSearchForm
    model = Book
    ordering = ['pk']
    paginate_by = 20

    def get_form_kwargs(self):
        return {'data': self.request.GET}

    def get_queryset(self):
        form = self.get_form()
        books = super().get_queryset()
        if form.is_valid():
            if title := form.cleaned_data.get('title'):
                books = books.filter(title__icontains=title)
            if author := form.cleaned_data.get('author'):
                books = books.filter(author__icontains=author)
            if isbn := form.cleaned_data.get('isbn'):
                books = books.filter(isbn__icontains=isbn)
            if category := form.cleaned_data.get('category'):
                books = books.filter(category=category)
        return books

    def get_context_data(self, **kwargs):
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        kwargs['querystring'] = urlencode(query_params)
        return super().get_context_data(**kwargs)


class BookDetailView(DetailView):
    model = Book


class BookCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'library.add_book'
    model = Book
    fields = '__all__'
    success_url = reverse_lazy('library:book-list')


class BookUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'library.change_book'
    model = Book
    fields = '__all__'
    success_url = reverse_lazy('library:book-list')


class BookDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'library.delete_book'
    model = Book
    success_url = reverse_lazy('library:book-list')


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if book.quantity > 0:
        BorrowRecord.objects.create(user=request.user, book=book)
        book.quantity -= 1
        book.save()
    return redirect('library:book-list')


@login_required
def renew_book(request, record_id):
    record = get_object_or_404(BorrowRecord, pk=record_id, user=request.user)
    record.renew()
    return redirect('library:borrow-records')


@login_required
def return_book(request, record_id):
    record = get_object_or_404(BorrowRecord, pk=record_id, user=request.user)
    record.return_book()
    return redirect('library:borrow-records')


@login_required
def borrow_records(request):
    borrow_record_list = BorrowRecord.objects.filter(user=request.user).order_by('-borrow_date')
    return render(request, 'library/borrow_record_list.html', {'borrow_record_list': borrow_record_list})


class AdminBorrowRecordListView(PermissionRequiredMixin, FormMixin, ListView):
    permission_required = 'library.view_borrowrecord'
    form_class = BorrowRecordSearchForm
    model = BorrowRecord
    ordering = ['-borrow_date']
    context_object_name = 'borrow_record_list'
    template_name = 'library/admin_borrow_record_list.html'

    def get_form_kwargs(self):
        return {'data': self.request.GET}

    def get_queryset(self):
        form = self.get_form()
        records = super().get_queryset()
        if form.is_valid():
            if username := form.cleaned_data.get('username'):
                records = records.filter(user__username=username)
            if isbn := form.cleaned_data.get('isbn'):
                records = records.filter(book__isbn=isbn)
        return records
