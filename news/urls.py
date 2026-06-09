from django.urls import path
from . import views, manage_views as mv

urlpatterns = [
    path('', views.home, name='home'),
    path('list/', views.news_list, name='news_list'),
    path('list/<int:category_id>/', views.news_list, name='news_list_by_category'),
    path('detail/<int:news_id>/', views.news_detail, name='news_detail'),
    path('search/', views.search, name='search'),
    path('img/', views.image_proxy, name='image_proxy'),
    path('detail/<int:news_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # 站内管理后台 /manage/
    path('manage/', mv.manage_dashboard, name='manage_dashboard'),
    path('manage/news/', mv.manage_news_list, name='manage_news_list'),
    path('manage/news/create/', mv.manage_news_create, name='manage_news_create'),
    path('manage/news/<int:news_id>/edit/', mv.manage_news_edit, name='manage_news_edit'),
    path('manage/news/<int:news_id>/delete/', mv.manage_news_delete, name='manage_news_delete'),
    path('manage/news/<int:news_id>/toggle-featured/', mv.manage_news_toggle_featured, name='manage_news_toggle_featured'),
    path('manage/category/', mv.manage_category_list, name='manage_category_list'),
    path('manage/category/create/', mv.manage_category_create, name='manage_category_create'),
    path('manage/category/<int:cat_id>/edit/', mv.manage_category_edit, name='manage_category_edit'),
    path('manage/category/<int:cat_id>/delete/', mv.manage_category_delete, name='manage_category_delete'),
    path('manage/users/', mv.manage_users_list, name='manage_users_list'),
    path('manage/users/<int:user_id>/edit/', mv.manage_user_edit, name='manage_user_edit'),
    path('manage/users/<int:user_id>/toggle-active/', mv.manage_user_toggle_active, name='manage_user_toggle_active'),
    path('manage/users/<int:user_id>/delete/', mv.manage_user_delete, name='manage_user_delete'),
]
