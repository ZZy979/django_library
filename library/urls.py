from django.urls import path
from . import views

app_name = 'library'
urlpatterns = [
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('books/', views.SearchBookView.as_view(), name='search-book'),
    path('book/<int:book_id>/borrow/', views.borrow_book, name='borrow-book'),
]
