from typing import Optional
from sqlalchemy import (
    Integer, String, Text, Float, Date, DateTime, 
    ForeignKey, MetaData, func, text
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Configuration du schéma "sae" par défaut
metadata_obj = MetaData(schema="sae")

class Base(DeclarativeBase):
    metadata = metadata_obj

# =================================================================================
# |-                            Tables principales
# =================================================================================

class Language(Base):
    __tablename__ = 'language'
    language_id: Mapped[int] = mapped_column(primary_key=True)
    language_name: Mapped[Optional[str]] = mapped_column(String(50))

class AlbumType(Base):
    __tablename__ = 'album_type'
    type_id: Mapped[int] = mapped_column(primary_key=True)
    type_name: Mapped[Optional[str]] = mapped_column(String(50))

class License(Base):
    __tablename__ = 'license'
    license_id: Mapped[int] = mapped_column(primary_key=True)
    license_name: Mapped[Optional[str]] = mapped_column(String(255))

class Tag(Base):
    __tablename__ = 'tag'
    tag_id: Mapped[int] = mapped_column(primary_key=True)
    tag_name: Mapped[Optional[str]] = mapped_column(String(255))

class Genre(Base):
    __tablename__ = 'genre'
    genre_id: Mapped[int] = mapped_column(primary_key=True)
    genre_parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey('sae.genre.genre_id', ondelete="CASCADE"))
    genre_title: Mapped[Optional[str]] = mapped_column(String(255))
    genre_handle: Mapped[Optional[str]] = mapped_column(String(255))
    genre_nb_tracks: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Relation auto-référentielle
    parent = relationship("Genre", remote_side=[genre_id])

class Platform(Base):
    __tablename__ = 'platform'
    platform_id: Mapped[int] = mapped_column(primary_key=True)
    platform_name: Mapped[Optional[str]] = mapped_column(String(50))

class Period(Base):
    __tablename__ = 'period'
    period_id: Mapped[int] = mapped_column(primary_key=True)
    period_interval: Mapped[Optional[str]] = mapped_column(String(50))

class Context(Base):
    __tablename__ = 'context'
    context_id: Mapped[int] = mapped_column(primary_key=True)
    context_name: Mapped[Optional[str]] = mapped_column(String(50))

class Mood(Base):
    __tablename__ = 'mood'
    mood_id: Mapped[int] = mapped_column(primary_key=True)
    mood_name: Mapped[Optional[str]] = mapped_column(String(50))

class Artist(Base):
    __tablename__ = 'artist'
    artist_id: Mapped[int] = mapped_column(primary_key=True)
    artist_handle: Mapped[Optional[str]] = mapped_column(String(50))
    artist_name: Mapped[Optional[str]] = mapped_column(String(50))
    artist_bio: Mapped[Optional[str]] = mapped_column(Text)
    artist_location: Mapped[Optional[str]] = mapped_column(String(255))
    artist_latitude: Mapped[Optional[float]] = mapped_column(Float)
    artist_longitude: Mapped[Optional[float]] = mapped_column(Float)
    artist_members: Mapped[Optional[str]] = mapped_column(String(255))
    artist_associated_labels: Mapped[Optional[str]] = mapped_column(String(255))
    artist_related_projects: Mapped[Optional[str]] = mapped_column(String(255))
    artist_active_year_begin: Mapped[Optional[int]] = mapped_column(Integer)
    artist_year_end: Mapped[Optional[int]] = mapped_column(Integer)
    artist_contact: Mapped[Optional[str]] = mapped_column(String(255))
    artist_favorites: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    artist_comments: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    artist_url: Mapped[Optional[str]] = mapped_column(String(255))
    artist_image_file: Mapped[Optional[str]] = mapped_column(String(255))

    # Relations
    tracks = relationship("Track", secondary="sae.artist_album_track", back_populates="artists", overlaps="albums,artists,tracks")
    albums = relationship("Album", secondary="sae.artist_album_track", back_populates="artists", overlaps="albums,artists,tracks")

class Album(Base):
    __tablename__ = 'album'
    album_id: Mapped[int] = mapped_column(primary_key=True)
    album_handle: Mapped[Optional[str]] = mapped_column(String(255))
    album_title: Mapped[Optional[str]] = mapped_column(String(255))
    album_information: Mapped[Optional[str]] = mapped_column(Text)
    album_date_created: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    album_date_released: Mapped[Optional[Date]] = mapped_column(Date)
    album_listens: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    album_favorites: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    album_comments: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    album_producer: Mapped[Optional[str]] = mapped_column(String(255))
    album_engineer: Mapped[Optional[str]] = mapped_column(String(255))
    album_image_file: Mapped[Optional[str]] = mapped_column(String(255))
    album_url: Mapped[Optional[str]] = mapped_column(String(255))
    type_id: Mapped[Optional[int]] = mapped_column(ForeignKey('sae.album_type.type_id', ondelete="SET NULL"))

    # Relations
    tracks = relationship("Track", secondary="sae.artist_album_track", back_populates="albums", overlaps="artists,albums,tracks")
    artists = relationship("Artist", secondary="sae.artist_album_track", back_populates="albums", overlaps="artists,albums,tracks")

class Track(Base):
    __tablename__ = 'track'
    track_id: Mapped[int] = mapped_column(primary_key=True)
    track_title: Mapped[Optional[str]] = mapped_column(String(255))
    track_duration: Mapped[Optional[float]] = mapped_column(Float)
    track_listens: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    track_favorites: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    track_interest: Mapped[Optional[float]] = mapped_column(Float)
    track_comments: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    track_date_created: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    track_date_recorded: Mapped[Optional[Date]] = mapped_column(Date)
    track_composer: Mapped[Optional[str]] = mapped_column(String(100))
    track_lyricist: Mapped[Optional[str]] = mapped_column(String(100))
    track_publisher: Mapped[Optional[str]] = mapped_column(String(100))
    license_id: Mapped[Optional[int]] = mapped_column(ForeignKey('sae.license.license_id', ondelete="SET NULL"))

    # Relations
    artists = relationship("Artist", secondary="sae.artist_album_track", back_populates="tracks", overlaps="artists,albums,tracks")
    albums = relationship("Album", secondary="sae.artist_album_track", back_populates="tracks", overlaps="artists,albums,tracks")
    playlists = relationship("Playlist", secondary="sae.playlist_track", back_populates="tracks")

class StatsEchonest(Base):
    __tablename__ = 'stats_echonest'
    track_id: Mapped[int] = mapped_column(ForeignKey('sae.track.track_id', ondelete="CASCADE"), primary_key=True)
    acousticness: Mapped[Optional[float]] = mapped_column(Float)
    danceability: Mapped[Optional[float]] = mapped_column(Float)
    energy: Mapped[Optional[float]] = mapped_column(Float)
    instrumentalness: Mapped[Optional[float]] = mapped_column(Float)
    liveness: Mapped[Optional[float]] = mapped_column(Float)
    speechness: Mapped[Optional[float]] = mapped_column(Float)
    tempo: Mapped[Optional[float]] = mapped_column(Float)
    valence: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[Optional[int]] = mapped_column(Integer)
    hotness: Mapped[Optional[int]] = mapped_column(Integer)

# =================================================================================
# |-                            Utilisateurs et derives
# =================================================================================

class User(Base):
    __tablename__ = 'user'
    user_id: Mapped[int] = mapped_column(primary_key=True)
    liked_tracks: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    image: Mapped[Optional[str]] = mapped_column(String(255))
    pseudo: Mapped[Optional[str]] = mapped_column(String(50))
    login: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    mdp: Mapped[str] = mapped_column(String(64), nullable=False)
    gender: Mapped[Optional[str]] = mapped_column(String(1)) # char
    birth_year: Mapped[Optional[Date]] = mapped_column(Date)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    situation_name: Mapped[Optional[str]] = mapped_column(String(50))
    frequency_interval: Mapped[Optional[str]] = mapped_column(String(50))
    last_calculated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    # Relations
    playlists = relationship("Playlist", back_populates="owner")

class SearchHistory(Base):
    __tablename__ = 'search_history'
    history_id: Mapped[int] = mapped_column(primary_key=True)
    history_query: Mapped[Optional[str]] = mapped_column(String(255))
    history_timestamp: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"))

class StatsUser(Base):
    __tablename__ = 'stats_user'
    stat_user_id: Mapped[int] = mapped_column(primary_key=True)
    danceability_affinity: Mapped[Optional[float]] = mapped_column(Float)
    energy_affinity: Mapped[Optional[float]] = mapped_column(Float)
    instrumentalness_affinity: Mapped[Optional[float]] = mapped_column(Float)
    liveness_affinity: Mapped[Optional[float]] = mapped_column(Float)
    speechness_affinity: Mapped[Optional[float]] = mapped_column(Float)
    tempo_affinity: Mapped[Optional[float]] = mapped_column(Float)
    valence_affinity: Mapped[Optional[float]] = mapped_column(Float)
    currency_affinity: Mapped[Optional[float]] = mapped_column(Float)
    hotness_affinity: Mapped[Optional[float]] = mapped_column(Float)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"), unique=True)

class Playlist(Base):
    __tablename__ = 'playlist'
    playlist_id: Mapped[int] = mapped_column(primary_key=True)
    playlist_name: Mapped[Optional[str]] = mapped_column(String(100))
    playlist_listens: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"))

    # Relations
    owner = relationship("User", back_populates="playlists")
    tracks = relationship("Track", secondary="sae.playlist_track", back_populates="playlists")

class ListeningHistory(Base):
    __tablename__ = 'listening_history'
    history_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"))
    playlist_id: Mapped[Optional[int]] = mapped_column(ForeignKey('sae.playlist.playlist_id', ondelete="CASCADE"))
    listened_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

# =================================================================================
# |-                        Relations (Tables de liaison)
# =================================================================================

class ArtistAlbumTrack(Base):
    __tablename__ = 'artist_album_track'
    artist_id: Mapped[int] = mapped_column(ForeignKey('sae.artist.artist_id', ondelete="CASCADE"), primary_key=True)
    album_id: Mapped[int] = mapped_column(ForeignKey('sae.album.album_id', ondelete="CASCADE"), primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey('sae.track.track_id', ondelete="CASCADE"), primary_key=True)

class PlaylistUserFavorite(Base):
    __tablename__ = 'playlist_user_favorite'
    user_id: Mapped[int] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"), primary_key=True)
    playlist_id: Mapped[int] = mapped_column(ForeignKey('sae.playlist.playlist_id', ondelete="CASCADE"), primary_key=True)
    added_at: Mapped[Optional[Date]] = mapped_column(Date, server_default=func.current_date())

class PlaylistUser(Base):
    __tablename__ = 'playlist_user'
    user_id: Mapped[int] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"), primary_key=True)
    playlist_id: Mapped[int] = mapped_column(ForeignKey('sae.playlist.playlist_id', ondelete="CASCADE"), primary_key=True)

class PlaylistTrack(Base):
    __tablename__ = 'playlist_track'
    playlist_id: Mapped[int] = mapped_column(ForeignKey('sae.playlist.playlist_id', ondelete="CASCADE"), primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey('sae.track.track_id', ondelete="CASCADE"), primary_key=True)

class UserContext(Base):
    __tablename__ = 'user_context'
    user_id: Mapped[int] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"), primary_key=True)
    context_id: Mapped[int] = mapped_column(ForeignKey('sae.context.context_id', ondelete="CASCADE"), primary_key=True)

class ScoreMood(Base):
    __tablename__ = 'score_mood'
    user_id: Mapped[int] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"), primary_key=True)
    mood_id: Mapped[int] = mapped_column(ForeignKey('sae.mood.mood_id', ondelete="CASCADE"), primary_key=True)
    affinity_score: Mapped[float] = mapped_column(Float, server_default=text("0"))

class UserPlatform(Base):
    __tablename__ = 'user_platform'
    user_id: Mapped[int] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"), primary_key=True)
    platform_id: Mapped[int] = mapped_column(ForeignKey('sae.platform.platform_id', ondelete="CASCADE"), primary_key=True)

class ScorePeriod(Base):
    __tablename__ = 'score_period'
    user_id: Mapped[int] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"), primary_key=True)
    period_id: Mapped[int] = mapped_column(ForeignKey('sae.period.period_id', ondelete="CASCADE"), primary_key=True)
    affinity_score: Mapped[float] = mapped_column(Float, server_default=text("0"))

class UserTrackListening(Base):
    __tablename__ = 'user_track_listening'
    user_id: Mapped[int] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"), primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey('sae.track.track_id', ondelete="CASCADE"), primary_key=True)
    nb_listening: Mapped[int] = mapped_column(Integer, server_default=text("1"))

class TrackUserFavorite(Base):
    __tablename__ = 'track_user_favorite'
    user_id: Mapped[int] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"), primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey('sae.track.track_id', ondelete="CASCADE"), primary_key=True)
    added_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

class TrackGenre(Base):
    __tablename__ = 'track_genre'
    track_id: Mapped[int] = mapped_column(ForeignKey('sae.track.track_id', ondelete="CASCADE"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey('sae.genre.genre_id', ondelete="CASCADE"), primary_key=True)

class TrackGenreMajoritaire(Base):
    __tablename__ = 'track_genre_majoritaire'
    track_id: Mapped[int] = mapped_column(ForeignKey('sae.track.track_id', ondelete="CASCADE"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey('sae.genre.genre_id', ondelete="CASCADE"), primary_key=True)

class GenreTopUser(Base):
    __tablename__ = 'genre_top_user'
    user_id: Mapped[int] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey('sae.genre.genre_id', ondelete="CASCADE"), primary_key=True)
    genre_rate: Mapped[Optional[float]] = mapped_column(Float)

class TrackLanguage(Base):
    __tablename__ = 'track_language'
    track_id: Mapped[int] = mapped_column(ForeignKey('sae.track.track_id', ondelete="CASCADE"), primary_key=True)
    language_id: Mapped[int] = mapped_column(ForeignKey('sae.language.language_id', ondelete="CASCADE"), primary_key=True)

class UserLanguage(Base):
    __tablename__ = 'user_language'
    user_id: Mapped[int] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"), primary_key=True)
    language_id: Mapped[int] = mapped_column(ForeignKey('sae.language.language_id', ondelete="CASCADE"), primary_key=True)

class AlbumTag(Base):
    __tablename__ = 'album_tag'
    album_id: Mapped[int] = mapped_column(ForeignKey('sae.album.album_id', ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey('sae.tag.tag_id', ondelete="CASCADE"), primary_key=True)

class TrackTag(Base):
    __tablename__ = 'track_tag'
    track_id: Mapped[int] = mapped_column(ForeignKey('sae.track.track_id', ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey('sae.tag.tag_id', ondelete="CASCADE"), primary_key=True)

class ArtistTag(Base):
    __tablename__ = 'artist_tag'
    artist_id: Mapped[int] = mapped_column(ForeignKey('sae.artist.artist_id', ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey('sae.tag.tag_id', ondelete="CASCADE"), primary_key=True)

class UserArtistFavorite(Base):
    __tablename__ = 'user_artist_favorite'
    artist_id: Mapped[int] = mapped_column(ForeignKey('sae.artist.artist_id', ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"), primary_key=True)

class ArtistLanguage(Base):
    __tablename__ = 'artist_language'
    artist_id: Mapped[int] = mapped_column(ForeignKey('sae.artist.artist_id', ondelete="CASCADE"), primary_key=True)
    language_id: Mapped[int] = mapped_column(ForeignKey('sae.language.language_id', ondelete="CASCADE"), primary_key=True)

class UserAlbumFavorite(Base):
    __tablename__ = 'user_album_favorite'
    user_id: Mapped[int] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"), primary_key=True)
    album_id: Mapped[int] = mapped_column(ForeignKey('sae.album.album_id', ondelete="CASCADE"), primary_key=True)
    added_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

class UserAlbumListening(Base):
    __tablename__ = 'user_album_listening'
    user_id: Mapped[int] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"), primary_key=True)
    album_id: Mapped[int] = mapped_column(ForeignKey('sae.album.album_id', ondelete="CASCADE"), primary_key=True)
    nb_listening: Mapped[Optional[int]] = mapped_column(Integer)

class UserPlaylistListening(Base):
    __tablename__ = 'user_playlist_listening'
    user_id: Mapped[int] = mapped_column(ForeignKey('sae.user.user_id', ondelete="CASCADE"), primary_key=True)
    playlist_id: Mapped[int] = mapped_column(ForeignKey('sae.playlist.playlist_id', ondelete="CASCADE"), primary_key=True)
    nb_listening: Mapped[Optional[int]] = mapped_column(Integer)

# =================================================================================
# |-                                    Vues
# =================================================================================
# Note: SQLAlchemy ne crée pas les vues via create_all(). 
# Ces classes servent à les interroger (SELECT).

class ViewUser(Base):
    __tablename__ = 'view_user'
    __table_args__ = {'info': {'is_view': True}}
    
    # On doit définir une PK artificielle pour que le mapper SQLAlchemy fonctionne
    user_id: Mapped[int] = mapped_column(primary_key=True)
    pseudo: Mapped[Optional[str]] = mapped_column(String(50))
    image: Mapped[Optional[str]] = mapped_column(String(255))
    situation_name: Mapped[Optional[str]] = mapped_column(String(50))

class ViewTrackMaterialise(Base):
    __tablename__ = 'view_track_materialise'
    __table_args__ = {'info': {'is_view': True, 'materialized': True}}

    track_id: Mapped[int] = mapped_column(primary_key=True)
    track_title: Mapped[Optional[str]] = mapped_column(String(255))
    track_duration: Mapped[Optional[float]] = mapped_column(Float)
    track_interest: Mapped[Optional[float]] = mapped_column(Float)
    track_comments: Mapped[Optional[int]] = mapped_column(Integer)
    track_date_created: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    track_date_recorded: Mapped[Optional[Date]] = mapped_column(Date)
    track_composer: Mapped[Optional[str]] = mapped_column(String(100))
    track_lyricist: Mapped[Optional[str]] = mapped_column(String(100))
    track_publisher: Mapped[Optional[str]] = mapped_column(String(100))
    license_id: Mapped[Optional[int]] = mapped_column(Integer)
    album_id: Mapped[Optional[int]] = mapped_column(Integer)
    album_title: Mapped[Optional[str]] = mapped_column(String(255))
    album_handle: Mapped[Optional[str]] = mapped_column(String(255))
    album_information: Mapped[Optional[str]] = mapped_column(Text)
    album_date_created: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    album_date_released: Mapped[Optional[Date]] = mapped_column(Date)
    album_engineer: Mapped[Optional[str]] = mapped_column(String(255))
    album_producer: Mapped[Optional[str]] = mapped_column(String(255))
    artist_id: Mapped[Optional[int]] = mapped_column(Integer)
    artist_name: Mapped[Optional[str]] = mapped_column(String(50))
    tags_list: Mapped[Optional[str]] = mapped_column(Text)
    genres_list: Mapped[Optional[str]] = mapped_column(Text)
    danceability: Mapped[Optional[float]] = mapped_column(Float)
    energy: Mapped[Optional[float]] = mapped_column(Float)
    tempo: Mapped[Optional[float]] = mapped_column(Float)
    languages_list: Mapped[Optional[str]] = mapped_column(Text)

class ViewFavoriteListens(Base):
    __tablename__ = 'view_favorite_listens'
    __table_args__ = {'info': {'is_view': True}}
    
    # PK composite artificielle pour le mapping car la vue n'en a pas
    track_id: Mapped[int] = mapped_column(primary_key=True)
    album_id: Mapped[int] = mapped_column(primary_key=True) 
    playlist_id: Mapped[int] = mapped_column(primary_key=True)
    
    track_listens: Mapped[Optional[int]] = mapped_column(Integer)
    track_favorites: Mapped[Optional[int]] = mapped_column(Integer)
    album_listens: Mapped[Optional[int]] = mapped_column(Integer)
    album_favorites: Mapped[Optional[int]] = mapped_column(Integer)
    playlist_listens: Mapped[Optional[int]] = mapped_column(Integer)
    playlist_favorites: Mapped[Optional[int]] = mapped_column(Integer)