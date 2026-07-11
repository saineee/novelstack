from django.contrib.auth import get_user_model
import pytest
from .forms import CreateUserForm



def test_duplicate_email_rejected(db):
    User = get_user_model()
    User.objects.create_user(username='testuser123', email='testuser@gmail.com', password='testuser123')
    form = CreateUserForm(data={
        'username': 'testuser123',
        'email': 'testuser@gmail.com',
        'password1': 'testuser123',
        'password2': 'testuser123',
    })
    assert form.is_valid() is False
    assert 'email' in form.errors
