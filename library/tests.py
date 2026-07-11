from django.db import IntegrityError
import pytest
from django.urls.base import reverse
from library.models import UserBook

def test_something(library_data):
    assert UserBook.objects.count() == 4
    assert library_data['user_one']['user'].username == 'user_one'

def test_reading_status_filter(client, library_data):
    client.force_login(user=library_data['user_one']['user'])
    response = client.get(reverse('library'), {'reading_status': 'hiatus'})
    assert response.context['books'][0].status == 'hiatus'
    assert len(response.context['books']) == 1

    response = client.get(reverse('library'), {'reading_status': 'finished'})
    assert len(response.context['books']) == 0

def test_library_scoped_to_user(client, library_data):
    client.force_login(user=library_data['user_one']['user'])
    response = client.get(reverse('library'))
    assert len(response.context['books']) == 2
    for ub in response.context['books']:
        assert ub.user == library_data['user_one']['user']


def test_title_filter(client, library_data):
    client.force_login(user=library_data['user_two']['user'])
    response = client.get(reverse('library'), {'title': 'zzz'})
    assert len(response.context['books']) == 0

    response = client.get(reverse('library'), {'title': 'Reverend'})
    assert len(response.context['books']) == 1
    assert response.context['books'][0].book.title == 'Reverend Insanity'

def test_publication_status_filter(client, library_data):
    client.force_login(user=library_data['user_two']['user'])
    response = client.get(reverse('library'), {'status': 'hiatus'})
    assert len(response.context['books']) == 0
    response = client.get(reverse('library'), {'status': 'completed'})
    assert len(response.context['books']) == 1
    assert response.context['books'][0].book.title == 'Reverend Insanity'

    client.force_login(user=library_data['user_one']['user'])
    response = client.get(reverse('library'), {'status': 'hiatus'})
    assert len(response.context['books']) == 0

def test_combined_filters(client, library_data):
    client.force_login(user=library_data['user_two']['user'])
    response = client.get(reverse('library'), {'status': 'completed', 'reading_status': 'reading'})
    assert len(response.context['books']) == 1
    assert response.context['books'][0].book.title == 'Reverend Insanity'
    assert response.context['books'][0].user == library_data['user_two']['user']
    response = client.get(reverse('library'), {'status': 'hiatus', 'reading_status': 'reading'})
    assert len(response.context['books']) == 0

    client.force_login(user=library_data['user_one']['user'])
    response = client.get(reverse('library'), {'status': 'completed', 'reading_status': 'hiatus'})
    assert len(response.context['books']) == 1
    assert response.context['books'][0].book.title == 'Reverend Insanity'

def test_profile_aggregation(client, library_data):
    client.force_login(user=library_data['user_one']['user'])
    response = client.get(reverse('profile'))
    assert response.context['total_books'] == 2
    assert response.context['total_chapters_read'] == 3000
    assert response.context['fav_genre'] in ('Xianxia', 'Fantasy')
    by_status = {row['status']: row['count'] for row in response.context['books_by_status']}
    assert by_status == {'hiatus': 1, 'dropped': 1}
    assert response.context['avg_rating'] == pytest.approx(4.0)

def test_userbook_uniqueness(library_data):
    user = library_data['user_one']['user']
    book = library_data['user_one']['books'][0].book
    with pytest.raises(IntegrityError):
        UserBook.objects.create(user=user, book=book, status='reading')