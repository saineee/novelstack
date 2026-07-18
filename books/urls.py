from .import views
from django.urls import path

urlpatterns = [path('', views.book_list, name='book_list'),
               path('create/', views.book_create, name='book_create'),
               path('<int:book_id>/edit/', views.book_update, name='book_update'),
               path('<int:book_id>/delete/', views.book_delete, name='book_delete'),
               path('<int:book_id>/details/', views.book_details, name='book_details'),
               path('search/', views.search, name='search'),
               path('import/<int:anilist_id>/', views.anilist_import, name='anilist_import')]