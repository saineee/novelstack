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
                                   status="completed")
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

@pytest.fixture
def book_data(db):
    book_one = Book.objects.create(title="Reverend Insanity", author="Gu Zhen Ren", description="Blank", chapters=2020, release_date="2018-01-01", classification="Webnovel",
                                   genre="Xianxia", status="completed")
    book_two = Book.objects.create(title="Mother of Learning", author="Unknown", description="Blank", chapters=100, release_date="2020-05-27",
                                   classification="Webnovel", genre="Fantasy", status="completed")
    book_three = Book.objects.create(title="Lord of the Mysteries", author="Cuttlefish who loves diving", description="Blank", chapters=1200, release_date="2017-01-23",
                                     classification="Webnovel", genre="Fantasy", status="ongoing")
    book_four = Book.objects.create(title="Shadow Slave", author="Guilty Three", description="Blank", chapters=3000, release_date="2019-06-07", classification="Webnovel",
                                    genre="Xuanhuan", status="ongoing")
    book_five = Book.objects.create(title="Lord of the Mysteries 2: Circle of Inevitability", author="Cuttlefish who loves diving", description="Blank", chapters=1100, release_date="2023-06-07",
                                    classification="Webnovel", genre="Xuanhuan", status="ongoing")
    return {
        'books': [book_one, book_two, book_three, book_four, book_five]
    }

@pytest.fixture
def user_data(db):
    user = get_user_model()
    staff_user = user.objects.create_user(username="jim", email="jim@gmail.com", password="jim12345j", is_staff=True)
    reg_user = user.objects.create_user(username="rob", email="rob@gmail.com", password="adsfhjasdf")

    return {
        'staff': staff_user,
        'reg': reg_user
    }