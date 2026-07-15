from pydantic import BaseModel, ConfigDict

class AnilistBase(BaseModel):
    model_config = ConfigDict(extra='forbid')

class StaffName(AnilistBase):
    full: str | None = None

class Staff(AnilistBase):
    name: StaffName | None = None

class StaffEdge(AnilistBase):
    node: Staff | None = None
    role: str | None = None

class StaffConnection(AnilistBase):
    edges: list[StaffEdge] | None = None

class MediaTitle(AnilistBase):
    romaji: str | None = None
    english: str | None = None

class FuzzyDate(AnilistBase):
    year: int | None = None
    month: int | None = None
    day: int | None = None

class MediaCoverImage(AnilistBase):
    large: str | None = None

class Media(AnilistBase):
    id: int
    title: MediaTitle | None = None
    chapters: int | None = None
    startDate: FuzzyDate | None = None
    format: str | None = None
    countryOfOrigin: str | None = None
    genres: list[str] | None = None
    status: str | None = None
    coverImage: MediaCoverImage | None = None
    staff: StaffConnection | None = None
    description: str | None = None