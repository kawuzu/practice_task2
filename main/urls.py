from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),  # Регистрация
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(), name='login'),  # Вход
    path('create_request/', views.create_request, name='create_request'),
    path('my_requests/', views.my_requests, name='my_requests'),  # Список заявок
    path('request/<int:request_id>/', views.request_detail, name='request_detail'),  # Страница заявки
    path('request/<int:id>/delete/', views.delete_request, name='delete_request'),
    path('requests/', views.all_requests, name='all_requests'),  # измененный URL для всех заявок
    path('check_username/', views.check_username, name='check_username'),
    path('request/<int:request_id>/change_status/', views.change_request_status, name='change_request_status'),
    path('categories/', views.all_categories, name='all_categories'),  # Список категорий
    path('category/create/', views.create_category, name='create_category'),  # Добавление категории
    path('category/<int:category_id>/edit/', views.edit_category, name='edit_category'),  # Редактирование категории
    path('category/<int:category_id>/delete/', views.delete_category, name='delete_category'),  # Удаление категории
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
