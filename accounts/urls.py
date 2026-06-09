from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('bookmark/<int:news_id>/toggle/', views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmarks/', views.bookmark_list, name='bookmark_list'),
    path('profile/', views.profile, name='profile'),
    path('password/change/', views.password_change, name='password_change'),
    path('avatar/upload/', views.avatar_upload, name='avatar_upload'),
    path('avatar/delete/', views.avatar_delete, name='avatar_delete'),
]
