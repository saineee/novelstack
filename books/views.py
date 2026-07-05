from django.shortcuts import render, redirect
from .models import Book
from .forms import BookForm

def book_list(request):
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books})

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
    book = Book.objects.get(id = book_id)
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
    book = Book.objects.get(id = book_id)
    if request.method == 'POST':
       book.delete()
       return redirect('book_list')
    else:
        return render(request, 'books/book_delete.html', {'book': book})