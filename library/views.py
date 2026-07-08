from django.db.models import Count, Sum, Avg
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

def userbook_delete(request, userbook_id):
    book = get_object_or_404(UserBook, id=userbook_id)
    if request.method == 'POST':
        book.delete()
        return redirect('library')
    else:
        return render(request, 'library/delete.html', {'userbook': book, 'userbook_id': userbook_id})

def profile(request):
     username = request.user.username
     date_joined = request.user.date_joined
     my_books = UserBook.objects.filter(user=request.user)
     total_books = my_books.count()
     total_chapters_read = my_books.aggregate(total=Sum('current_chapter'))['total']
     avg_rating = my_books.aggregate(avg = Avg('rating'))['avg']
     books_by_status = my_books.values('status').annotate(count=Count('id'))
     retrieve_fav_genre = my_books.values('book__genre').annotate(count=Count('id')).order_by('-count')
     top = retrieve_fav_genre.first()
     fav_genre = top.get("book__genre") if top else None
     return render(request, 'library/profile.html', {'username': username, 'date_joined': date_joined,
                                                     'my_books': my_books, 'total_books': total_books, 'total_chapters_read': total_chapters_read,
                                                     'avg_rating': avg_rating, 'books_by_status': books_by_status, 'fav_genre': fav_genre})