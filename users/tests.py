from django.urls.base import reverse
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

def test_profile_aggregation(client, library_data):
    client.force_login(user=library_data['user_one']['user'])
    response = client.get(reverse('profile'))
    assert response.context['total_books'] == 2
    assert response.context['total_chapters_read'] == 3000
    assert response.context['fav_genre'] == 'Action'
    by_status = {row['status']: row['count'] for row in response.context['books_by_status']}
    assert by_status == {'hiatus': 1, 'dropped': 1}
    assert response.context['avg_rating'] == pytest.approx(4.0)