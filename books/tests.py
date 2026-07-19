from books.models import Book, Genre
from django.urls.base import reverse

def test_no_filter_return_all_books(client, book_data):
    response = client.get(reverse('book_list'))
    assert len(response.context['books']) == 5
    assert response.status_code == 200

def test_title_filter(client, book_data):
    response = client.get(reverse('book_list'), {'title': 'lord'})
    query_results = {b.title for b in response.context['books']}
    expected = {"Lord of the Mysteries", "Lord of the Mysteries 2: Circle of Inevitability"}
    assert query_results == expected

def test_genre_xuanhuan_filter(client, book_data):
    response = client.get(reverse('book_list'), {'genre': 'Xuanhuan'})
    query_results = {b.title for b in response.context['books']}
    expected = {"Reverend Insanity", "Shadow Slave"}
    assert query_results == expected

def test_genre_fantasy_filter(client, book_data):
    response = client.get(reverse('book_list'), {'genre': 'Fantasy'})
    query_results = {b.title for b in response.context['books']}
    expected = {"Lord of the Mysteries 2: Circle of Inevitability", "Lord of the Mysteries"}
    assert query_results == expected

def test_status_filter_completed(client, book_data):
    response = client.get(reverse('book_list'), {'status': 'completed'})
    query_results = {b.title for b in response.context['books']}
    expected = {"Reverend Insanity", "Mother of Learning"}
    assert query_results == expected

def test_status_filter_ongoing(client, book_data):
    response = client.get(reverse('book_list'), {'status': 'ongoing'})
    query_results = {b.title for b in response.context['books']}
    expected = {"Lord of the Mysteries 2: Circle of Inevitability", "Lord of the Mysteries", "Shadow Slave"}
    assert query_results == expected

def test_combined_filters(client, book_data):
    response = client.get(reverse('book_list'), {'genre': 'Fantasy', 'status': 'completed'})
    query_results = {b.title for b in response.context['books']}
    expected = set()
    assert query_results == expected

def test_book_details_anon(client, book_data):
    response = client.get(reverse('book_details', kwargs={'book_id': book_data['books'][0].id}))
    assert response.status_code == 200
    assert response.context['already_exists'] == False

def test_book_create_reg(client, user_data):
    client.force_login(user=user_data['reg'])
    response = client.get(reverse('book_create'))
    assert response.status_code == 302

def test_book_create_staff(client, user_data):
    client.force_login(user=user_data['staff'])
    response = client.get(reverse('book_create'))
    assert response.status_code == 200

def test_book_update_reg(client, user_data, book_data):
    client.force_login(user=user_data['reg'])
    response = client.get(reverse('book_update', kwargs={'book_id': book_data['books'][0].id}))
    assert response.status_code == 302

def test_book_update_staff(client, user_data, book_data):
    client.force_login(user=user_data['staff'])
    response = client.get(reverse('book_update', kwargs={'book_id': book_data['books'][0].id}))
    assert response.status_code == 200

def test_book_delete_reg(client, user_data, book_data):
    client.force_login(user=user_data['reg'])
    response = client.get(reverse('book_delete', kwargs={'book_id': book_data['books'][0].id}))
    assert response.status_code == 302

def test_book_delete_staff(client, user_data, book_data):
    client.force_login(user=user_data['staff'])
    response = client.get(reverse('book_delete', kwargs={'book_id': book_data['books'][0].id}))
    assert response.status_code == 200

def test_add_to_library_anon(client, book_data):
    response = client.get(reverse('add_to_library', kwargs={'book_id': book_data['books'][0].id}))
    assert response.status_code == 302

def test_book_create_staff_post(client, user_data):
    client.force_login(user=user_data['staff'])
    wuxia = Genre.objects.create(name="Wuxia")
    client.post(reverse('book_create'), {'title': 'Nano Machine', 'author': 'idk', 'description': 'Blank', 'chapters': 1000,
                                                       'release_date': '2020-01-11', 'classification': 'Webnovel', 'genres': [wuxia.pk], 'status': 'completed'})
    assert Book.objects.filter(title='Nano Machine').exists() is True

def test_book_delete_staff_post(client, user_data, book_data):
    client.force_login(user=user_data['staff'])
    book_id = book_data['books'][0].id
    client.post(reverse('book_delete', kwargs={'book_id': book_id}))