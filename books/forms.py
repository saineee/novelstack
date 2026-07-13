from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('title', 'author', 'description', 'chapters', 'release_date',
                  'classification', 'genre', 'status')
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'})
        }