# your_app/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'app' 

urlpatterns = [
    path('', views.file_list, name='file_list'),
    path('<int:item_id>/', views.detail, name='detail'),
    path('file/create', views.create_file, name='create_file'),
    path('like_file/<int:item_id>/', views.like_file, name='like_file'),
    path('comment_create/<int:file_id>/', views.comment_create, name='comment_create'),
    path('file_modify/<int:item_id>/', views.file_modify, name='file_modify'),
    path('file_delete/<int:item_id>/', views.file_delete, name='file_delete'),
    path('comment_modify/<int:comment_id>/', views.comment_modify, name='comment_modify'),
    path('comment_delete/<int:comment_id>/', views.comment_delete, name='comment_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
