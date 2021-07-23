from django.shortcuts import render, get_object_or_404
from django.views import generic

from .models import Author, Book


def index(request):
    return render(request, 'library/index.html')


class AuthorListView(generic.ListView):

    def get_queryset(self):
        if 'name' in self.request.GET:
            return Author.objects.filter(name__contains=self.request.GET['name'])
        else:
            return Author.objects.all()


class AuthorDetailView(generic.DetailView):
    model = Author


class BookListView(generic.ListView):

    def get_queryset(self):
        if 'title' in self.request.GET:
            return Book.objects.filter(title__contains=self.request.GET['title'])
        else:
            return Book.objects.all()


class BookDetailView(generic.DetailView):
    model = Book


class BooksOfAuthorView(generic.ListView):

    def get_queryset(self):
        author = get_object_or_404(Author, pk=self.request.GET['aid'])
        return author.book_set.all()
