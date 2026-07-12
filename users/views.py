from django.db.models.aggregates import Sum, Avg, Count
from django.shortcuts import render, redirect
from library.models import UserBook
from .forms import CreateUserForm

def register(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            return render(request, 'users/registration.html', {'form': form})
    else:
        form = CreateUserForm()
    return render(request, 'users/registration.html', {'form': form})

def profile(request):
    username = request.user.username
    date_joined = request.user.date_joined
    my_books = UserBook.objects.filter(user=request.user)
    total_books = my_books.count()
    total_chapters_read = my_books.aggregate(total=Sum('current_chapter'))['total']
    avg_rating = my_books.aggregate(avg=Avg('rating'))['avg']
    books_by_status = my_books.values('status').annotate(count=Count('id'))
    retrieve_fav_genre = my_books.values('book__genre').annotate(count=Count('id')).order_by('-count')
    top = retrieve_fav_genre.first()
    fav_genre = top.get("book__genre") if top else None
    return render(request, 'users/profile.html', {'username': username, 'date_joined': date_joined,
                                                    'my_books': my_books, 'total_books': total_books,
                                                    'total_chapters_read': total_chapters_read,
                                                    'avg_rating': avg_rating, 'books_by_status': books_by_status,
                                                    'fav_genre': fav_genre})
