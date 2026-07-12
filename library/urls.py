from django.urls import path
from . import views

urlpatterns = [
    path('', views.library, name='library'),
    path('<int:book_id>/add_to_library/', views.add_to_library, name='add_to_library'),
    path('', views.library, name='library'),
    path('<int:userbook_id>/update/', views.userbook_update, name='userbook_update'),
    path('<int:userbook_id>/delete/', views.userbook_delete, name='userbook_delete'),
]