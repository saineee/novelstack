from datetime import date
from django.utils.html import strip_tags

STATUS_MAP = {
    "FINISHED": "completed",
    "RELEASING": "ongoing",
    "HIATUS": "hiatus",
    "CANCELLED": "cancelled",
    "NOT_YET_RELEASED": "not_yet_released",
}

CLASSIFICATION_MAP = {
    ("MANGA", "CN"): "Manhua",
    ("MANGA", "KR"): "Manhwa",
    ("MANGA", "JP"): "Manga",
    ("NOVEL", "JP"): "Light Novel",
}


def mapped_candidates(media):
    title = None
    if media.title:
        title = media.title.english or media.title.romaji

    description = None
    if media.description is not None:
        description = strip_tags(media.description)

    chapters = media.chapters

    status = STATUS_MAP.get(media.status)

    genres = media.genres #this will return a list of strings, BookForm.genres requries the genres.pks, not the name

    release_date = None
    if media.startDate:
        year = media.startDate.year
        month = media.startDate.month
        day = media.startDate.day
        if all(v is not None for v in (year, month, day)):
            release_date = date(year, month, day)

    target = "Story" if media.format == "NOVEL" else "Original Story" #story is used if media type is a novel for author, if an adapation, Original Story is used, can also have more than one, which a human check will have to fix
    author = None
    if media.staff is not None and media.staff.edges is not None:
        for edge in media.staff.edges:
            if edge.role == target:
                author = edge.node.name.full
                break

    classification = CLASSIFICATION_MAP.get((media.format, media.countryOfOrigin))

    anilist_id = media.id

    anilist_cover_url = None
    if media.coverImage:
        anilist_cover_url = media.coverImage.large

    mapped_vals = {
        "title": title,
        "author": author,
        "description": description,
        "chapters": chapters,
        "release_date": release_date,
        "classification": classification,
        "genres": genres,
        "status": status,
        "anilist_id": anilist_id,
        "anilist_cover_url": anilist_cover_url,
    }

    return mapped_vals