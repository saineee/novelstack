from django import forms
from .models import UserBook


class UserBookForm(forms.ModelForm):
    class Meta:
        model = UserBook
        fields = ('current_chapter', 'status', 'rating', 'date_started', 'date_ended')

        widgets = {
            'date_started': forms.DateInput(attrs={'type': 'date'}),
            'date_ended': forms.DateInput(attrs={'type': 'date'})
        }
    def __init__(self, *args, **kwargs):
        super(UserBookForm, self).__init__(*args, **kwargs)
    #clean is used because we are checking constraints between tables, and django's CheckConstraint can't span tables
    def clean(self):
        cleaned_data = super().clean()
        date_started = cleaned_data.get('date_started')
        release_date = self.instance.book.release_date
        current_chapter = cleaned_data.get('current_chapter')
        total_chapters = self.instance.book.chapters

        if current_chapter is not None and total_chapters is not None:
            if current_chapter > total_chapters:
                self.add_error('current_chapter',
                               f'Progress ({current_chapter}) cannot exceed {self.instance.book.title}\'s total chapters ({total_chapters})')

        if date_started is not None and release_date is not None:
            if date_started < release_date:
                self.add_error('date_started', f'The date {date_started} is before {self.instance.book.title}\'s release date: {release_date}')