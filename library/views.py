from books.models import Book
from django.shortcuts import render,get_object_or_404, redirect
from .models import UserBook


def add_to_library(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        UserBook.objects.create(book=book, user=request.user)
        return redirect('book_details', book_id=book_id)
    else:
        return redirect('book_details', book_id=book_id)