from books.models import Book, Genre
from django.urls.base import reverse


def test_search_no_title(client, user_data):
    client.force_login(user=user_data['staff'])
    response = client.get(reverse('search'))
    assert response.context['candidates'] == []
    assert response.context['searched'] is False
    assert response.context['search_failed'] is False

def test_search_returns_candidates(client, user_data, monkeypatch):
    fake_response = {
        "data": {"Page": {"media": [
            {"id": 102, "title": {"romaji": "TEST", "english": "TESTeng"}}
        ]}}
    }
    monkeypatch.setattr('books.views.fetch_candidates', lambda title: fake_response)
    client.force_login(user=user_data['staff'])
    response = client.get(reverse('search'), {'title': 'test'})
    assert len(response.context['candidates']) == 1

def test_search_returns_candidates_already_exists_true(client, db, user_data, monkeypatch):
    Book.objects.create(title='test', anilist_id="105", author="test", classification="Webnovel")
    fake_response = {
        "data": {"Page": {"media": [
            {"id": 105, "title": {"romaji": "TEST", "english": "test"}}
        ]}}
    }
    monkeypatch.setattr('books.views.fetch_candidates', lambda title: fake_response)
    client.force_login(user=user_data['staff'])
    response = client.get(reverse('search'), {'title': 'test'})
    assert response.context['candidates'][0]['exists'] is True

def test_search_returns_candidates_already_exists_false(client, db, user_data, monkeypatch):
    fake_response = {
        "data": {"Page": {"media": [
            {"id": 105, "title": {"romaji": "TEST", "english": "test"}}
        ]}}
    }
    monkeypatch.setattr('books.views.fetch_candidates', lambda title: fake_response)
    client.force_login(user=user_data['staff'])
    response = client.get(reverse('search'), {'title': 'test'})
    assert response.context['candidates'][0]['exists'] is False

def test_search_returns_none_fetch_failure(monkeypatch, client, user_data):
    monkeypatch.setattr('books.views.fetch_candidates', lambda title: None)
    client.force_login(user=user_data['staff'])
    response = client.get(reverse('search'), {'title': 'test'})
    assert response.context['candidates'] == []
    assert response.context['search_failed'] is True

def test_search_redirect_non_staff(client, user_data):
    client.force_login(user=user_data['reg'])
    response = client.get(reverse('search'))
    assert response.status_code == 302

def test_import_post(client, user_data, monkeypatch, db):
    fake = {"data": {"Media": {"id": 105, "coverImage": {"large": "https://x/cover.jpg"}}}}
    monkeypatch.setattr('books.views.fetch_id', lambda anilist_id: fake)
    genre = Genre.objects.create(name="Action")
    client.force_login(user=user_data['staff'])
    response = client.post(reverse('anilist_import', args=[105]), {
        'title': 'test book',
        'author': 'someone',
        'classification': 'Webnovel',
        'chapters': 100,
        'genres': [genre.pk],
        'status': 'ongoing'
    })
    assert Book.objects.filter(anilist_id="105").exists()
    book = Book.objects.get(anilist_id="105")
    assert book.anilist_cover_url == "https://x/cover.jpg"
    assert book.title == "test book"
    assert list(book.genres.all()) == [genre]
    assert response.status_code == 302

def test_import_redirect_non_staff(client, user_data):
    client.force_login(user=user_data['reg'])
    response = client.post(reverse('anilist_import', args=[105]))
    assert response.status_code == 302
