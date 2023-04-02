from django.urls import path
from . import views


app_name = 'about'

urlpatterns = [
    path('', views.AboutAuthorView.as_view(), name='author'),
    path('author/', views.AboutAuthorView.as_view(), name='author'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
]
