from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.index, name='posts_home_page'),
    path('projects/', views.creativity, name='creativity'),
    path('projects/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.post_create, name='post_create'),
    path('projects/<int:post_id>/edit/', views.post_edit, name='post_edit'),
]
