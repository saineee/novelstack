from django import forms
from .models import UserBook
class UserBookForm(forms.ModelForm):
    class Meta:
        model = UserBook
        fields = ('current_chapter', 'status', 'rating', 'date_started', 'date_ended')