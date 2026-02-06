from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker, joinedload
from sqlalchemy import create_engine
from typing import List
import models, schema

from models import ( 
    Album, User, Playlist, Track, ListeningHistory, UserAlbumListening, UserPlaylistListening,
    PlaylistUserFavorite, TrackUserFavorite, UserArtistFavorite, UserAlbumFavorite, PlaylistUser,
    PlaylistTrack
)

from schema import (    
    UserCreate, PlaylistCreate, ListeningHistoryCreate, UserAlbumListeningCreate, UserPlaylistListeningCreate,
    PlaylistUserFavoriteCreate, TrackUserFavoriteCreate, UserArtistFavoriteCreate, UserAlbumFavoriteCreate, PlaylistUserCreate,
    PlaylistTrackCreate
)

import uvicorn
import os


###########################################
##             CONFIGURATION             ##
###########################################

app = FastAPI()

# Configuration BDD
db_host = os.getenv("DB_HOST", "localhost")
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "uJ7A\postgres",
    "host": "localhost",
    "port": "5432"
}

DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

engine = create_engine(DATABASE_URL)
       
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

###########################################
##               ROUTES                  ##
###########################################


######## GET ##

@app.get("/album") 
def get_all_albums(db: Session = Depends(get_db)):
    return db.query(Album).all()

@app.get("/album/{album_id}") 
def get_one_album(album_id: int, db: Session = Depends(get_db)):
    album = db.query(Album).filter(Album.album_id == album_id).first()
    
    if album is None:
        raise HTTPException(status_code=404, detail="Album non trouvé")
        
    return album

@app.get("/track") 
def get_all_track(db: Session = Depends(get_db)):
    return db.query(Track).all()

@app.get("/playlist") 
def get_all_track(db: Session = Depends(get_db)):
    return db.query(Playlist).all()


@app.get("/user/{email}")
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return user

@app.get("/playlists/user/{user_id}", response_model=List[schema.Playlist], include_in_schema=False)
def get_user_playlists(user_id: int, db: Session = Depends(get_db)):
    """
    Récupère les playlists d'un utilisateur spécifique.
    Caché de la doc (usage interne).
    """
    playlists = db.query(models.Playlist).filter(models.Playlist.user_id == user_id).options(joinedload(models.Playlist.tracks)).all()
    return playlists

# --- Routes Publiques (Données de référence) ---

@app.get("/genres", response_model=List[schema.Genre])
def get_all_genres(db: Session = Depends(get_db)):
    """Récupère tous les genres musicaux (pour filtres/navigation)."""
    return db.query(models.Genre).all()

@app.get("/tags", response_model=List[schema.Tag])
def get_all_tags(db: Session = Depends(get_db)):
    """Récupère tous les tags (pour recherche avancée)."""
    return db.query(models.Tag).all()

# --- Routes Utilisateur Privées (Cachées) ---

@app.get("/users/{user_id}/favorites/tracks", response_model=List[schema.Track], include_in_schema=False)
def get_user_favorite_tracks(user_id: int, db: Session = Depends(get_db)):
    """
    Récupère les pistes favorites d'un utilisateur.
    Caché de la doc (usage interne).
    """
    # Jointure via la table TrackUserFavorite
    favorites = db.query(models.Track).join(
        models.TrackUserFavorite, 
        models.Track.track_id == models.TrackUserFavorite.track_id
    ).filter(
        models.TrackUserFavorite.user_id == user_id
    ).options(joinedload(models.Track.artists)).all()
    return favorites

@app.get("/users/{user_id}/favorites/artists", response_model=List[schema.Artist], include_in_schema=False)
def get_user_favorite_artists(user_id: int, db: Session = Depends(get_db)):
    """
    Récupère les artistes favoris d'un utilisateur.
    Caché de la doc (usage interne).
    """
    favorites = db.query(models.Artist).join(
        models.UserArtistFavorite,
        models.Artist.artist_id == models.UserArtistFavorite.artist_id
    ).filter(
        models.UserArtistFavorite.user_id == user_id
    ).options(joinedload(models.Artist.albums)).all()
    return favorites

@app.get("/users/{user_id}/favorites/albums", response_model=List[schema.Album], include_in_schema=False)
def get_user_favorite_albums(user_id: int, db: Session = Depends(get_db)):
    """
    Récupère les albums favoris d'un utilisateur.
    Caché de la doc (usage interne).
    """
    favorites = db.query(models.Album).join(
        models.UserAlbumFavorite,
        models.Album.album_id == models.UserAlbumFavorite.album_id
    ).filter(
        models.UserAlbumFavorite.user_id == user_id
    ).options(joinedload(models.Album.tracks)).all()
    return favorites

@app.get("/users/{user_id}/listening-history", response_model=List[schema.ListeningHistory], include_in_schema=False)
def get_user_listening_history(user_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """
    Récupère l'historique d'écoute d'un utilisateur (playlists écoutées).
    Caché de la doc (usage interne).
    """
    history = db.query(models.ListeningHistory).filter(
        models.ListeningHistory.user_id == user_id
    ).options(joinedload(models.ListeningHistory.playlist)).order_by(
        models.ListeningHistory.listened_at.desc()
    ).offset(skip).limit(limit).all()
    return history

@app.get("/users/{user_id}/top-tracks", response_model=List[schema.TrackWithListenings], include_in_schema=False)
def get_user_top_tracks(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """
    Récupère les pistes les plus écoutées par l'utilisateur.
    Caché de la doc (usage interne).
    """
    top_tracks = db.query(
        models.Track,
        models.UserTrackListening.nb_listening
    ).join(
        models.UserTrackListening,
        models.Track.track_id == models.UserTrackListening.track_id
    ).filter(
        models.UserTrackListening.user_id == user_id
    ).options(joinedload(models.Track.artists)).order_by(
        models.UserTrackListening.nb_listening.desc()
    ).limit(limit).all()
    
    result = []
    for track, nb_listening in top_tracks:
        track_dict = {
            "track_id": track.track_id,
            "track_title": track.track_title,
            "track_duration": track.track_duration,
            "track_listens": track.track_listens,
            "track_favorites": track.track_favorites,
            "track_interest": track.track_interest,
            "track_date_created": track.track_date_created,
            "track_date_recorded": track.track_date_recorded,
            "track_composer": track.track_composer,
            "nb_listening": nb_listening,
            "artists": track.artists
        }
        result.append(track_dict)
    return result

@app.get("/users/{user_id}/top-albums", response_model=List[schema.AlbumWithListenings], include_in_schema=False)
def get_user_top_albums(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """
    Récupère les albums les plus écoutés par l'utilisateur.
    Caché de la doc (usage interne).
    """
    top_albums = db.query(
        models.Album,
        models.UserAlbumListening.nb_listening
    ).join(
        models.UserAlbumListening,
        models.Album.album_id == models.UserAlbumListening.album_id
    ).filter(
        models.UserAlbumListening.user_id == user_id
    ).options(joinedload(models.Album.tracks)).order_by(
        models.UserAlbumListening.nb_listening.desc()
    ).limit(limit).all()
    
    result = []
    for album, nb_listening in top_albums:
        album_dict = {
            "album_id": album.album_id,
            "album_title": album.album_title,
            "album_handle": album.album_handle,
            "album_information": album.album_information,
            "album_date_released": album.album_date_released,
            "album_listens": album.album_listens,
            "album_favorites": album.album_favorites,
            "album_producer": album.album_producer,
            "album_image_file": album.album_image_file,
            "nb_listening": nb_listening,
            "tracks": album.tracks
        }
        result.append(album_dict)
    return result

@app.get("/users/{user_id}/listening-stats", response_model=schema.UserListeningStats, include_in_schema=False)
def get_user_listening_stats(user_id: int, db: Session = Depends(get_db)):
    """
    Récupère les statistiques globales d'écoute de l'utilisateur.
    Caché de la doc (pour page statistiques).
    """
    from sqlalchemy import func
    
    # Total écoutes pistes
    total_tracks = db.query(func.sum(models.UserTrackListening.nb_listening)).filter(
        models.UserTrackListening.user_id == user_id
    ).scalar() or 0
    
    # Total écoutes albums
    total_albums = db.query(func.sum(models.UserAlbumListening.nb_listening)).filter(
        models.UserAlbumListening.user_id == user_id
    ).scalar() or 0
    
    # Total écoutes playlists
    total_playlists = db.query(func.sum(models.UserPlaylistListening.nb_listening)).filter(
        models.UserPlaylistListening.user_id == user_id
    ).scalar() or 0
    
    # Nombre de pistes uniques écoutées
    unique_tracks = db.query(func.count(models.UserTrackListening.track_id)).filter(
        models.UserTrackListening.user_id == user_id
    ).scalar() or 0
    
    # Nombre d'albums uniques écoutés
    unique_albums = db.query(func.count(models.UserAlbumListening.album_id)).filter(
        models.UserAlbumListening.user_id == user_id
    ).scalar() or 0
    
    # Nombre de playlists uniques écoutées
    unique_playlists = db.query(func.count(models.UserPlaylistListening.playlist_id)).filter(
        models.UserPlaylistListening.user_id == user_id
    ).scalar() or 0
    
    return {
        "total_track_listenings": total_tracks,
        "total_album_listenings": total_albums,
        "total_playlist_listenings": total_playlists,
        "total_unique_tracks": unique_tracks,
        "total_unique_albums": unique_albums,
        "total_unique_playlists": unique_playlists
    }

@app.get("/users/{user_id}/stats", response_model=schema.StatsUser, include_in_schema=False)
def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    """
    Récupère les affinités musicales calculées de l'utilisateur.
    Caché de la doc (pour graphique profil musical).
    """
    stats = db.query(models.StatsUser).filter(models.StatsUser.user_id == user_id).first()
    if not stats:
        raise HTTPException(status_code=404, detail="Stats utilisateur non trouvées")
    return stats


###########################################
##              POST                     ##
###########################################

@app.post("/user", status_code=201)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    new_user = User(**user_data.model_dump())
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post("/playlist", status_code=201)
def create_playlist(playlist_data: PlaylistCreate, db: Session = Depends(get_db)):
    new_playlist = Playlist(**playlist_data.model_dump())
    
    db.add(new_playlist)
    db.commit()
    db.refresh(new_playlist)
    
    return new_playlist

@app.post("/listeningHistory", status_code=201)
def create_listening_history(listening_history_data: ListeningHistoryCreate, db: Session = Depends(get_db)):
    new_listening_history = ListeningHistory(**listening_history_data.model_dump())
    
    db.add(new_listening_history)
    db.commit()
    db.refresh(new_listening_history)
    
    return new_listening_history

@app.post("/UserAlbumListening", status_code=201)
def create_user_album_listening(user_album_listening_data: UserAlbumListeningCreate, db: Session = Depends(get_db)):
    new_user_album_listening = UserAlbumListening(**user_album_listening_data.model_dump())
    
    db.add(new_user_album_listening)
    db.commit()
    db.refresh(new_user_album_listening)
    
    return new_user_album_listening

@app.post("/UserPlaylistListening", status_code=201)
def create_user_playlist_listening(user_album_listening_data: UserPlaylistListeningCreate, db: Session = Depends(get_db)):
    new_user_playlist_listening = UserPlaylistListening(**user_album_listening_data.model_dump())
    
    db.add(new_user_playlist_listening)
    db.commit()
    db.refresh(new_user_playlist_listening)
    
    return new_user_playlist_listening

@app.post("/PlaylistUserFavorite", status_code=201)
def create_playlist_user_favorite(playlist_user_favorite_data: PlaylistUserFavoriteCreate, db: Session = Depends(get_db)):
    new_playlist_user_favorite = PlaylistUserFavorite(**playlist_user_favorite_data.model_dump())
    
    db.add(new_playlist_user_favorite)
    db.commit()
    db.refresh(new_playlist_user_favorite)
    
    return new_playlist_user_favorite

@app.post("/TrackUserFavorite", status_code=201)
def create_track_user_favorite(track_user_favorite_data: TrackUserFavoriteCreate, db: Session = Depends(get_db)):
    new_track_user_favorite = TrackUserFavorite(**track_user_favorite_data.model_dump())
    
    db.add(new_track_user_favorite)
    db.commit()
    db.refresh(new_track_user_favorite)
    
    return new_track_user_favorite

@app.post("/UserArtistFavorite", status_code=201)
def create_user_artist_favorite(user_artist_favorite_data: UserArtistFavoriteCreate, db: Session = Depends(get_db)):
    new_user_artist_favorite = UserArtistFavorite(**user_artist_favorite_data.model_dump())
    
    db.add(new_user_artist_favorite)
    db.commit()
    db.refresh(new_user_artist_favorite)
    
    return new_user_artist_favorite

@app.post("/UserAlbumFavorite", status_code=201)
def create_user_album_favorite(user_album_favorite_data: UserAlbumFavoriteCreate, db: Session = Depends(get_db)):
    new_user_album_favorite = UserAlbumFavorite(**user_album_favorite_data.model_dump())
    
    db.add(new_user_album_favorite)
    db.commit()
    db.refresh(new_user_album_favorite)
    
    return new_user_album_favorite

@app.post("/PlaylistUser", status_code=201)
def create_playlist_user(playlist_user_data: PlaylistUserCreate, db: Session = Depends(get_db)):
    new_playlist_user = PlaylistUser(**playlist_user_data.model_dump())
    
    db.add(new_playlist_user)
    db.commit()
    db.refresh(new_playlist_user)
    
    return new_playlist_user

@app.post("/PlaylistTrack", status_code=201)
def create_playlist_track(playlist_track_data: PlaylistTrackCreate, db: Session = Depends(get_db)):
    new_playlist_track = PlaylistTrack(**playlist_track_data.model_dump())
    
    db.add(new_playlist_track)
    db.commit()
    db.refresh(new_playlist_track)
    
    return new_playlist_track


###########################################
##              DELETE                   ##
###########################################

@app.delete("/user/{user_id}", status_code=200)
def anonymize_user(user_id: int, db: Session = Depends(get_db)):
    """
    Anonymise les données personnelles d'un utilisateur (RGPD - Droit à l'oubli).
    Les statistiques d'écoute sont conservées de manière anonyme.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Anonymisation des données identifiables
    user.email = f"deleted_user_{user_id}@anonyme.fr"
    user.user_login = f"deleted_user_{user_id}"
    user.pseudo = f"Utilisateur supprimé"
    user.user_mdp = "ACCOUNT_DELETED" 
    user.image = None
    user.birth_year = None
    
    db.commit()
    
    return {"message": "Données personnelles anonymisées conformément au RGPD"}

@app.delete("/users/{user_id}/favorites/tracks/{track_id}", status_code=200)
def remove_favorite_track(user_id: int, track_id: int, db: Session = Depends(get_db)):
    """Retire une piste des favoris de l'utilisateur."""
    favorite = db.query(TrackUserFavorite).filter(
        TrackUserFavorite.user_id == user_id,
        TrackUserFavorite.track_id == track_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favori non trouvé")
    
    db.delete(favorite)
    db.commit()
    return {"message": "Titre retiré des favoris"}

@app.delete("/users/{user_id}/favorites/artists/{artist_id}", status_code=200)
def remove_favorite_artist(user_id: int, artist_id: int, db: Session = Depends(get_db)):
    """Retire un artiste des favoris de l'utilisateur."""
    favorite = db.query(UserArtistFavorite).filter(
        UserArtistFavorite.user_id == user_id,
        UserArtistFavorite.artist_id == artist_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favori non trouvé")
    
    db.delete(favorite)
    db.commit()
    return {"message": "Artiste retiré des favoris"}

@app.delete("/users/{user_id}/favorites/albums/{album_id}", status_code=200)
def remove_favorite_album(user_id: int, album_id: int, db: Session = Depends(get_db)):
    """Retire un album des favoris de l'utilisateur."""
    favorite = db.query(UserAlbumFavorite).filter(
        UserAlbumFavorite.user_id == user_id,
        UserAlbumFavorite.album_id == album_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favori non trouvé")
    
    db.delete(favorite)
    db.commit()
    return {"message": "Album retiré des favoris"}

@app.delete("/playlists/{playlist_id}", status_code=200)
def delete_playlist(playlist_id: int, db: Session = Depends(get_db)):
    """Supprime une playlist (et ses liens avec les pistes via CASCADE)."""
    playlist = db.query(Playlist).filter(Playlist.playlist_id == playlist_id).first()
    
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist non trouvée")
    
    db.delete(playlist)
    db.commit()
    return {"message": "Playlist supprimée"}

@app.delete("/playlists/{playlist_id}/tracks/{track_id}", status_code=200)
def remove_track_from_playlist(playlist_id: int, track_id: int, db: Session = Depends(get_db)):
    """Retire une piste d'une playlist."""
    link = db.query(PlaylistTrack).filter(
        PlaylistTrack.playlist_id == playlist_id,
        PlaylistTrack.track_id == track_id
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Piste non présente dans cette playlist")
    
    db.delete(link)
    db.commit()
    return {"message": "Piste retirée de la playlist"}


###########################################
##      AUTORISATIONS & LANCEMENT        ##
###########################################

# --- Configuration CORS ---
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
