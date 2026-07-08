from django.shortcuts import render, redirect, get_object_or_404
from library.models import UserBook
from .models import Book
from .forms import BookForm

# book creation form - if form valid save to db, if not, render page with existing info and error message
def book_create(request):
    is_update = False
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
        return render(request, 'books/book_form.html', {'form': form, 'is_update': is_update})
    else:
        form = BookForm()
        return render(request,'books/book_form.html',{'form': form, 'is_update':is_update})

def book_update(request, book_id):
    is_update = True
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
       form = BookForm(request.POST, instance=book)
       if form.is_valid():
           form.save()
           return redirect('book_list')
       return render(request, 'books/book_form.html', {'form': form, 'is_update': is_update})
    else:
        form = BookForm(instance=book)
        return render(request, 'books/book_form.html', {'form': form, 'is_update':is_update})

def book_delete(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
       book.delete()
       return redirect('book_list')
    else:
        return render(request, 'books/book_delete.html', {'book': book})

def book_details(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    already_exists = UserBook.objects.filter(book=book, user=request.user).exists()
    return render(request, 'books/book_details.html', {'book': book, 'already_exists': already_exists})

def book_list(request):
    sorted_books = Book.objects.order_by('title')
    title = request.GET.get('title')
    genre = request.GET.get('genre')
    status = request.GET.get('status')
    if title:
        sorted_books = sorted_books.filter(title__icontains=title)
    if genre:
        sorted_books = sorted_books.filter(genre__icontains=genre)
    if status:
        sorted_books = sorted_books.filter(status = status)
    return render(request, 'books/book_list.html', {'books': sorted_books})

