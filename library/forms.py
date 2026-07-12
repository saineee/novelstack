from django import forms
from .models import UserBook


class UserBookForm(forms.ModelForm):
    class Meta:
        model = UserBook
        fields = ('current_chapter', 'status', 'rating', 'date_started', 'date_ended')

    def clean(self):
        cleaned_data = super().clean()
        date_started = cleaned_data.get('date_started')
        release_date = self.instance.book.release_date

        if date_started is not None and release_date is not None:
            if date_started < release_date:
                self.add_error('date_started', f'The date {date_started} is before {self.instance.book.title}\'s release date: {release_date}')