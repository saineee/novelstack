from .views import book_list, book_create
from django.urls import path

urlpatterns = [path('', book_list, name='book_list'),
               path('create/', book_create, name='book_create'),]