from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date, datetime

##########################################
##             SCHÉMAS GET              ##
##########################################

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
    

# ==================== Listening Stats Schemas ====================

class TrackWithListenings(TrackBase):
    """Piste avec nombre d'écoutes de l'utilisateur."""
    track_id: int
    nb_listening: int
    artists: List[ArtistBase] = []

    class Config:
        from_attributes = True

class AlbumWithListenings(AlbumBase):
    """Album avec nombre d'écoutes de l'utilisateur."""
    album_id: int
    nb_listening: int
    tracks: List[TrackBase] = []

    class Config:
        from_attributes = True

class UserListeningStats(BaseModel):
    """Statistiques globales d'écoute d'un utilisateur."""
    total_track_listenings: int
    total_album_listenings: int
    total_playlist_listenings: int
    total_unique_tracks: int
    total_unique_albums: int
    total_unique_playlists: int
    

##########################################
##             SCHÉMAS POST             ##
##########################################


# ==================== User Schemas ====================

class UserCreate(BaseModel):
    email: EmailStr
    user_login: str
    user_mdp: str
    pseudo: Optional[str] = None
    user_gender: Optional[str] = None
    birth_year: Optional[date] = None
    situation_name: Optional[str] = None
    frequency_interval: Optional[str] = None

# ==================== Playlist Schemas =================

class PlaylistCreate(BaseModel):
    playlist_name: str

# ==================== ListeningHistory Schemas =========

class ListeningHistoryCreate(BaseModel):
    playlist_id: int

# ==================== UserTrackListening Schemas =======

class UserTrackListeningCreate(BaseModel):
    track_id: int

# ==================== UserAlbumListening Schemas =======

class UserAlbumListeningCreate(BaseModel):
    album_id: int

# ==================== UserPlaylistListening Schemas ====

class UserPlaylistListeningCreate(BaseModel):
    playlist_id: int

# ==================== PlaylistUserFavorite Schemas =====

class PlaylistUserFavoriteCreate(BaseModel):
    playlist_id: int

# ==================== TrackUserFavorite Schemas ========

class TrackUserFavoriteCreate(BaseModel):
    track_id: int

# ==================== UserArtistFavorite Schemas =======

class UserArtistFavoriteCreate(BaseModel):
    artist_id: int

# ==================== UserAlbumFavorite Schemas ========

class UserAlbumFavoriteCreate(BaseModel):
    album_id: int

# ==================== PlaylistUser Schemas =============

class PlaylistUserCreate(BaseModel):
    playlist_id: int

# ==================== PlaylistTrack Schemas ============

class PlaylistTrackCreate(BaseModel):
    playlist_id: int
    track_id: int

# ==================== UserTrackListening Schemas ============

class UserTrackListeningCreate(BaseModel):
    track_id: int


##########################################
##            SCHÉMAS PATCH             ##
##########################################

# ==================== User Schemas ============

class UserUpdate(BaseModel):
    current_password: str

    image: Optional[str] = None
    pseudo: Optional[str] = None
    new_mdp: Optional[str] = None
    user_gender: Optional[str] = None # char
    situation_name: Optional[str] = None
    frequency_interval: Optional[str] = None

# ==================== Playlist Schemas ============

class PlaylistUpdate(BaseModel):
    playlist_name: Optional[str]
    
# ==================== UserTrackListening Schemas ============

class UserTrackListeningUpdate(BaseModel):
    nb_listening: int

# ==================== UserAlbumListening Schemas ============

class UserAlbumListeningUpdate(BaseModel):
    nb_listening: int

# ==================== UserPlaylistListening Schemas ============

class UserPlaylistListeningUpdate(BaseModel):
    nb_listening: int