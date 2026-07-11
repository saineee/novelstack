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