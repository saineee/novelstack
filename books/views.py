from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from library.models import UserBook
from pydantic import ValidationError
from .anilist import fetch_candidates, fetch_id
from .anilist_mapping import mapped_candidates
from .anilist_schema import Media
from .models import Book, Genre
from .forms import BookForm
import logging
logger = logging.getLogger("novelstack")

# book creation requires staff privileges, regular users cannot access this form.
@staff_member_required
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

# updating a book entry requires staff privileges, regular users cannot update the book object itself.
@staff_member_required
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

# book deletion requires staff privileges, regular users cannot delete the book object itself.
@staff_member_required
def book_delete(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
       book.delete()
       return redirect('book_list')
    else:
        return render(request, 'books/book_delete.html', {'book': book})

def book_details(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if not request.user.is_authenticated: #anon users do not have a library. guard the fk query, which would crash on anon user access
        already_exists = False
    else:
        already_exists = UserBook.objects.filter(book=book, user=request.user).exists()
    return render(request, 'books/book_details.html', {'book': book, 'already_exists': already_exists})

def book_list(request):
    sorted_books = Book.objects.order_by('title')
    title = request.GET.get('title', '')
    genre = request.GET.get('genre', '')
    status = request.GET.get('status', '')
    genres = Genre.objects.all()
    status_choices = Book.STATUS_CHOICES
    # status, genres is exact-match (fixed choice dropdown), title uses icontains for partial text search
    if title:
        sorted_books = sorted_books.filter(title__icontains=title)
    if genre:
        sorted_books = sorted_books.filter(genres__name=genre)
    if status:
        sorted_books = sorted_books.filter(status=status)
    return render(request, 'books/book_list.html', {'genres': genres, 'books': sorted_books, 'title': title, 'status': status, 'status_choices': status_choices, 'genre': genre})

def home(request):
    return render(request, 'home.html')

@staff_member_required
def search(request):
    title = request.GET.get('title')
    if title:
        searched = True
        response = fetch_candidates(title)
        if response is None:
            candidates = []
            search_failed = True
        else:
            validated = []
            for candidate in response['data']['Page']['media']:
                try:
                    validated.append(Media.model_validate(candidate))
                except ValidationError as e:
                    logger.error(e)
            candidate_ids = [str(m.id) for m in validated]
            existing_ids = set(Book.objects.filter(anilist_id__in=candidate_ids).values_list('anilist_id', flat=True))
            candidates = [{"media": m, "exists": str(m.id) in existing_ids} for m in validated]
            search_failed = False
    else:
        candidates = []
        search_failed = False
        searched = False

    return render(request, 'books/import_search.html', {'candidates': candidates, 'search_failed': search_failed, 'searched': searched})

@staff_member_required
def anilist_import(request, anilist_id):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            response = fetch_id(anilist_id)
            if response is None:
                return redirect('search')
            media = Media.model_validate(response['data']['Media'])
            book.anilist_id = media.id
            book.anilist_cover_url = media.coverImage.large if media.coverImage else None
            book.save()
            form.save_m2m()
            return redirect('book_list')
    else:
        response = fetch_id(anilist_id)
        if response is None:
            return redirect('search')
        try:
            validated = Media.model_validate(response['data']['Media'])
        except ValidationError as e:
            logger.error(e)
            return redirect('search')

        mapped = mapped_candidates(validated)
        genre_pks = []
        if mapped['genres']:
            for name in mapped['genres']:
                genre, created = Genre.objects.get_or_create(name=name)
                genre_pks.append(genre.pk)

        mapped['genres'] = genre_pks
        form = BookForm(initial=mapped)

    return render(request, 'books/import_review.html', {'form': form})

