from django.shortcuts import render, get_object_or_404
from django.views import generic

from library.models import Author, Book


# Create your views here.

def index(request):
    return render(request, 'library/index.html')


class AuthorListView(generic.ListView):
    template_name = 'library/author-list.html'
    context_object_name = 'author_list'

    def get_queryset(self):
        if 'name' in self.request.GET:
            return Author.objects.filter(name__contains=self.request.GET['name'])
        else:
            return Author.objects.all()


class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'library/author-detail.html'


class BookListView(generic.ListView):
    template_name = 'library/book-list.html'
    context_object_name = 'book_list'

    def get_queryset(self):
        if 'title' in self.request.GET:
            return Book.objects.filter(title__contains=self.request.GET['title'])
        else:
            return Book.objects.all()


class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'library/book-detail.html'


class BooksOfAuthorView(generic.ListView):
    template_name = 'library/book-list.html'
    context_object_name = 'book_list'

    def get_queryset(self):
        author = get_object_or_404(Author, pk=self.request.GET['aid'])
        return author.book_set.all()
