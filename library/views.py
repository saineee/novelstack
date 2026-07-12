from django.contrib.auth.decorators import login_required
from books.models import Book
from django.shortcuts import render,get_object_or_404, redirect
from .models import UserBook
from .forms import UserBookForm


@login_required
def add_to_library(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        UserBook.objects.create(book=book, user=request.user)
        return redirect('book_details', book_id=book_id)
    else:
        return redirect('book_details', book_id=book_id)

def library(request):
    books = UserBook.objects.filter(user=request.user)
    title = request.GET.get('title', '')
    genre = request.GET.get('genre','')
    status = request.GET.get('status', '')
    reading_status = request.GET.get('reading_status', '')
    status_choices = Book.STATUS_CHOICES
    status_choices_userbook = UserBook.STATUS_CHOICES
    if title:
        books=books.filter(book__title__icontains=title)
    if genre:
        books=books.filter(book__genre__icontains=genre)
    if status:
        books=books.filter(book__status=status)
    if reading_status:
        books=books.filter(status=reading_status)
    return render(request, 'library/library.html', {'books': books, 'title': title, 'genre': genre, 'status': status,
                                                    'reading_status': reading_status, 'status_choices_userbook': status_choices_userbook, 'status_choices': status_choices})

def userbook_update(request, userbook_id):
    userbook = get_object_or_404(UserBook, id=userbook_id)
    if request.method == 'POST':
        form = UserBookForm(request.POST, instance = userbook)
        if form.is_valid():
            form.save()
            return redirect('library')
        else:
            return render(request, 'library/update.html', {'form': form, "userbook_id": userbook_id})
    else:
        form = UserBookForm(instance = userbook)
        return render(request, 'library/update.html', {'form': form, "userbook_id": userbook_id})

def userbook_delete(request, userbook_id):
    book = get_object_or_404(UserBook, id=userbook_id)
    if request.method == 'POST':
        book.delete()
        return redirect('library')
    else:
        return render(request, 'library/delete.html', {'userbook': book, 'userbook_id': userbook_id})
