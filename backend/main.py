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