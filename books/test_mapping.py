from datetime import date

from books.anilist_schema import Media, MediaTitle, StaffConnection, Staff, StaffEdge, StaffName, FuzzyDate
from books.anilist_mapping import mapped_candidates

def test_title_prefer_eng():
    media = Media(id=1, title=MediaTitle(romaji="Blah", english="BlahEng"))
    result = mapped_candidates(media)
    assert result['title'] == 'BlahEng'

def test_title_eng_null_fallback_romaji():
    media = Media(id=1, title=MediaTitle(romaji="present", english=None))
    result = mapped_candidates(media)
    assert result['title'] == 'present'

def test_title_missing():
    media = Media(id=1)
    result = mapped_candidates(media)
    assert result['title'] is None

def test_title_both_null():
    media = Media(id=1, title=MediaTitle(romaji=None, english=None))
    result = mapped_candidates(media)
    assert result['title'] is None

def test_adaptation_uses_original_story():
    media = Media(id=1, format="MANGA", staff=StaffConnection(edges=[StaffEdge(role="Story", node=Staff(name=StaffName(full="testtest"))), StaffEdge(role="Original Story", node=Staff(name=StaffName(full="omae wa mou shindeiru"))), StaffEdge(role="Art", node=Staff(name=StaffName(full="I hate tests")))]))
    result = mapped_candidates(media)
    assert result['author'] == 'omae wa mou shindeiru'

def test_novel_uses_story():
    media = Media(id=1, format="NOVEL", staff=StaffConnection(edges=[StaffEdge(role="Illustration", node=Staff(name=StaffName(full="wrong"))), StaffEdge(role="Story", node=Staff(name=StaffName(full="testa")))]))
    result = mapped_candidates(media)
    assert result['author'] == 'testa'

def test_novel_uses_story_first_match():
    media = Media(id=1, format="NOVEL", staff=StaffConnection(edges=[StaffEdge(role="Illustration", node=Staff(name=StaffName(full="wrong"))), StaffEdge(role="Story", node=Staff(name=StaffName(full="testa1"))), StaffEdge(role="Story", node=Staff(name=StaffName(full="testa2")))]))
    result = mapped_candidates(media)
    assert result['author'] == 'testa1'

def test_novel_no_story_returns_none():
    media = Media(id=1, format="NOVEL", staff=StaffConnection(edges=[StaffEdge(role="Publisher", node=Staff(name=StaffName(full="tester2")))]))
    result = mapped_candidates(media)
    assert result['author'] is None

def test_author_on_no_staff():
    media = Media(id=1, format="NOVEL")
    result = mapped_candidates(media)
    assert result['author'] is None

def test_release_date_valid_fuzzy_date():
    media = Media(id=1, startDate=FuzzyDate(year=2020, month=1, day=1))
    result = mapped_candidates(media)
    assert result['release_date'] == date(year=2020, month=1, day=1)

def test_release_date_none_on_fuzzy_date_missing_year():
    media = Media(id=1, startDate=FuzzyDate(month=1, day=1))
    result = mapped_candidates(media)
    assert result['release_date'] is None

def test_classification_manhwa():
    media = Media(id=1, format="MANGA", countryOfOrigin="KR")
    result = mapped_candidates(media)
    assert result['classification'] == 'Manhwa'

def test_classification_manhwa_unrecognized_combo():
    media = Media(id=1, format="MANGA", countryOfOrigin="KRi")
    result = mapped_candidates(media)
    assert result['classification'] is None

def test_description_strips_html_tags():
    media = Media(id=1, description="Hello <br> everyone <div>")
    result = mapped_candidates(media)
    assert "<br>" not in result['description']
    assert result['description'] == "Hello  everyone "