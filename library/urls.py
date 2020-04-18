from django.urls import path

from . import views

app_name = 'library'
urlpatterns = [
    path('', views.index, name='index'),
    path('query-author/', views.AuthorListView.as_view(), name='query-author'),
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('query-book/', views.BookListView.as_view(), name='query-book'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('books-of-author/', views.BooksOfAuthorView.as_view(), name='books-of-author'),
]
