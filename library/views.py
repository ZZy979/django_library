from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView

from .models import Book, BorrowRecord


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


class BookListView(ListView):
    def get_queryset(self):
        if query := self.request.GET.get('q'):
            return Book.objects.filter(title__icontains=query)
        else:
            return Book.objects.all()


def borrow_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if book.quantity > 0:
        BorrowRecord.objects.create(user=request.user, book=book)
        book.quantity -= 1
        book.save()
    return redirect('library:book-list')
