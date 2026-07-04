from .views import book_list, book_create, book_update
from django.urls import path

urlpatterns = [path('', book_list, name='book_list'),
               path('create/', book_create, name='book_create'),
               path('<int:book_id>/edit', book_update, name='book_update'),]