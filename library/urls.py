from django.urls import path
from .views import add_to_library

urlpatterns = [
    path('<int:book_id>/add_to_library', add_to_library, name='add_to_library'),
]