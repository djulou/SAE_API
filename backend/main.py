from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker, joinedload
from sqlalchemy import create_engine
from typing import List
import models, schema

import uvicorn
import os

app = FastAPI()

# Configuration BDD
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_Config = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "admin",
    "host": DB_HOST,
    "port": "5432"
}
DATABASE_URL = f"postgresql://{DB_Config['user']}:{DB_Config['password']}@{DB_Config['host']}:{DB_Config['port']}/{DB_Config['dbname']}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Création des tables (si nécessaire)
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "API SAE connectée. Utilisez /docs pour voir les endpoints."}

@app.get("/albums", response_model=List[schema.Album]) 
def get_all_albums(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Récupère tous les albums avec leurs pistes (paginé)."""
    return db.query(models.Album).options(joinedload(models.Album.tracks)).offset(skip).limit(limit).all()

@app.get("/tracks", response_model=List[schema.Track])
def get_all_tracks(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Récupère toutes les pistes avec leurs artistes (paginé)."""
    return db.query(models.Track).options(joinedload(models.Track.artists)).offset(skip).limit(limit).all()

@app.get("/artists", response_model=List[schema.Artist])
def get_all_artists(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Récupère tous les artistes avec leurs albums (paginé)."""
    return db.query(models.Artist).options(joinedload(models.Artist.albums)).offset(skip).limit(limit).all()

# --- Routes basées sur les Vues ---

@app.get("/tracks/details", response_model=List[schema.TrackView])
def get_tracks_detailed(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Récupère les pistes avec détails (album, artiste) via une vue matérialisée."""
    return db.query(models.ViewTrackMaterialise).offset(skip).limit(limit).all()

"""
J'ai caché les endpoints /users/{user_id} et /playlists/user/{user_id} de la doc 
pour pouvoir les afficher, il faut changer include_in_schema=False 
en include_in_schema=True
"""

@app.get("/users/{user_id}", response_model=schema.UserProfile, include_in_schema=False)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """
    Récupère le profil complet d'un utilisateur (pour affichage sur page profil).
    Caché de la doc car réservé à l'usage interne / authentifié.
    """
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
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