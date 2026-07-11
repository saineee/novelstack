from django.contrib.auth import get_user_model
from books.models import Book
from library.models import UserBook

import pytest


@pytest.fixture
def library_data(db):
    user = get_user_model()
    user_one = user.objects.create_user(username='user_one', email='userone@gmail.com', password='user12345')
    user_two = user.objects.create_user(username='user_two', email='usertwo@gmail.com', password='usertwo12345')
    book_one = Book.objects.create(title="Reverend Insanity", author="Gu Zhen Ren", description="Blank", chapters=2000,
                                   release_date="2018-01-01", classification="Webnovel", genre="Xianxia",
                                   status="ended")
    book_two = Book.objects.create(title="Shadow Slave", author="Guilty Three",
                                   description="Growing up in poverty, Sunny never expected anything good from life.",
                                   chapters=3092, release_date="2020-01-01",
                                   classification="Webnovel", genre="Fantasy", status="ongoing")

    userbook_one = UserBook.objects.create(user=user_one, book=book_one, current_chapter=1000, status="hiatus",
                                           rating=6, date_started="2024-01-01", date_ended=None)
    userbook_two = UserBook.objects.create(user=user_two, book=book_two, current_chapter=1500, status="reading",
                                           rating=10, date_started="2026-01-05", date_ended=None)
    userbook_three = UserBook.objects.create(user=user_one, book=book_two, current_chapter=2000, status="dropped",
                                             rating=2, date_started="2024-01-05", date_ended="2026-02-05")
    userbook_four = UserBook.objects.create(user=user_two, book=book_one, current_chapter=1200, status="reading",
                                            rating=7, date_started="2025-05-07", date_ended=None)

    return {
        'user_one': {'user': user_one, 'books': [userbook_one, userbook_three]},
        'user_two': {'user': user_two, 'books': [userbook_two, userbook_four]},
    }
