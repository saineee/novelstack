from books.anilist_schema import Media, MediaTitle, StaffConnection, Staff, StaffEdge, StaffName
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