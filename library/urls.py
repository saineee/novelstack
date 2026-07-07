from django.urls import path
from .views import add_to_library, library, userbook_update

urlpatterns = [
    path('<int:book_id>/add_to_library', add_to_library, name='add_to_library'),
    path('', library, name='library'),
    path('<int:userbook_id>/update', userbook_update, name='userbook_update')
]