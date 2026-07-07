from books.models import Book
from django.shortcuts import render,get_object_or_404, redirect
from .models import UserBook
from .forms import UserBookForm

def add_to_library(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        UserBook.objects.create(book=book, user=request.user)
        return redirect('book_details', book_id=book_id)
    else:
        return redirect('book_details', book_id=book_id)

def library(request):
    books = UserBook.objects.filter(user=request.user)
    return render(request, 'library/library.html', {'books': books})

def userbook_update(request, userbook_id):
    book = get_object_or_404(UserBook, id=userbook_id)
    if request.method == 'POST':
        form = UserBookForm(request.POST, instance = book)
        if form.is_valid():
            form.save()
            return redirect('library')
        else:
            return render(request, 'library/update.html', {'form': form, "userbook_id": userbook_id})
    else:
        form = UserBookForm(instance = book)
        return render(request, 'library/update.html', {'form': form, "userbook_id": userbook_id})