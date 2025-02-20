from django.urls import path
from . import views

app_name = 'library'
urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('book/<int:book_id>/borrow/', views.borrow_book, name='borrow-book'),
]
