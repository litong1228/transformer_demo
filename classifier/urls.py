from django.urls import path
from . import views

urlpatterns = [
    path('text/', views.classify_text, name='classify_text'),
    path('text/api/', views.classify_text_api, name='classify_text_api'),
    path('batch/', views.batch_classify, name='batch_classify'),
    path('batch/<int:batch_id>/export/', views.export_batch, name='export_batch'),
    path('history/', views.classification_history, name='classification_history'),
]
