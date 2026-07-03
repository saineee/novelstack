from .views import book_list
from django.urls import path

urlpatterns = [path('', book_list, name='book_list'),]