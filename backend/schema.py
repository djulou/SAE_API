from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

# ==================== Artist Schemas ====================
class ArtistBase(BaseModel):
    artist_name: Optional[str] = None
    artist_handle: Optional[str] = None
    artist_bio: Optional[str] = None
    artist_location: Optional[str] = None
    artist_favorites: int = 0
    artist_comments: int = 0

# ==================== Album Schemas ====================
class AlbumBase(BaseModel):
    album_title: Optional[str] = None
    album_handle: Optional[str] = None
    album_information: Optional[str] = None
    album_date_released: Optional[date] = None
    album_listens: int = 0
    album_favorites: int = 0
    album_producer: Optional[str] = None
    album_image_file: Optional[str] = None

# ==================== Track Schemas ====================
class TrackBase(BaseModel):
    track_title: Optional[str] = None
    track_duration: Optional[float] = None
    track_listens: int = 0
    track_favorites: int = 0
    track_interest: Optional[float] = None
    track_date_created: datetime
    track_date_recorded: Optional[date] = None
    track_composer: Optional[str] = None

# ==================== Extended Schemas (with relations) ====================

class Artist(ArtistBase):
    artist_id: int
    albums: List[AlbumBase] = []

    class Config:
        from_attributes = True

class Album(AlbumBase):
    album_id: int
    tracks: List[TrackBase] = []
    
    class Config:
        from_attributes = True

class Track(TrackBase):
    track_id: int
    artists: List[ArtistBase] = []
    
    class Config:
        from_attributes = True

# ==================== Views Schemas ====================

class TrackView(BaseModel):
    track_id: int
    track_title: Optional[str] = None
    track_duration: Optional[float] = None
    track_interest: Optional[float] = None
    album_id: Optional[int] = None
    album_title: Optional[str] = None
    artist_id: Optional[int] = None
    artist_name: Optional[str] = None
    genres_list: Optional[str] = None
    tempo: Optional[float] = None

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    """Profil complet d'un utilisateur (sans mot de passe)."""
    user_id: int
    pseudo: Optional[str] = None
    email: str
    image: Optional[str] = None
    birth_year: Optional[date] = None
    situation_name: Optional[str] = None
    frequency_interval: Optional[str] = None
    liked_tracks: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== Playlist Schemas ====================

class PlaylistBase(BaseModel):
    playlist_name: Optional[str] = None
    playlist_listens: int = 0
    user_id: Optional[int] = None

class Playlist(PlaylistBase):
    playlist_id: int
    tracks: List[TrackBase] = []

    class Config:
        from_attributes = True
    