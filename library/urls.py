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
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
]
