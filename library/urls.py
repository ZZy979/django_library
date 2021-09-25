from django.urls import path

from . import views

app_name = 'library'
urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),

    path('', views.index, name='index'),
    # 读者视图
    path('search/', views.search, name='search'),
    path('search-book/', views.SearchBookView.as_view(), name='search-book'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),

    # 管理员视图
    path('book/list/', views.ListBookView.as_view(), name='list-book'),
    path('book/<int:pk>/change/', views.ChangeBookView.as_view(), name='change-book'),
]
