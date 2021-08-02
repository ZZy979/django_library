from django.urls import path

from . import views

app_name = 'library'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search, name='search'),
    path('search-book/', views.SearchBookView.as_view(), name='search-book'),
    path('search-author/', views.SearchAuthorView.as_view(), name='search-author'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('books-of-author/', views.BooksOfAuthorView.as_view(), name='books-of-author'),
]
