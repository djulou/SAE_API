from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, or_, func, text
import time

import time
import bcrypt

from models import ( 
    Album, User, Playlist, Track, Artist, ArtistAlbumTrack, ListeningHistory, UserAlbumListening, UserPlaylistListening,
    PlaylistUserFavorite, TrackUserFavorite, UserArtistFavorite, UserAlbumFavorite, PlaylistUser,
    PlaylistTrack, UserTrackListening, SearchHistory, ViewTrackMaterialise, ArtistAlbumTrack, ListeningHistory,
    Role, Permission
)

import schema

# 2. On importe les classes spécifiques pour tes fonctions de création
from schema import (    
    UserCreate, PlaylistCreate, ListeningHistoryCreate, UserAlbumListeningCreate, 
    UserPlaylistListeningCreate, PlaylistUserFavoriteCreate, TrackUserFavoriteCreate, 
    UserArtistFavoriteCreate, UserAlbumFavoriteCreate, PlaylistUserCreate,
    PlaylistTrackCreate, UserTrackListeningCreate, SearchHistoryCreate, TrackView,
    UserUpdate, PlaylistUpdate, UserTrackListeningUpdate, UserAlbumListeningUpdate, 
    UserPlaylistListeningUpdate
)

import uvicorn
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import pandas as pd

load_dotenv()



# Configuration JWT
SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError("La SECRET_KEY n'a pas été trouvée. Vérifiez votre fichier .env")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)


###########################################
##             CONFIGURATION             ##
###########################################

app = FastAPI()


###########################################
##      AUTORISATIONS & LANCEMENT        ##
###########################################

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

# Configuration BDD
db_host = os.getenv("DB_HOST", "localhost")
DB_CONFIG = {
    "dbname": "mabase",
    "user": "user",
    "password": "password",
    "host": "db",
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

def hash_password(password: str):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    password_byte = plain_password.encode('utf-8')
    hashed_byte = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte, hashed_byte)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

def has_permission(required_permission: str):
    """Vérifie si l'utilisateur a le droit d'effectuer une action via ses rôles."""
    def permission_checker(current_user: User = Depends(get_current_user)):
        # On extrait toutes les permissions de tous les rôles de l'utilisateur
        user_permissions = {p.permission_label for r in current_user.roles for p in r.permissions}
        
        # Un ADMIN a souvent tous les droits par défaut (optionnel)
        user_roles = {r.role_name for r in current_user.roles}
        
        if "ADMIN" not in user_roles and required_permission not in user_permissions:
            raise HTTPException(
                status_code=403, 
                detail=f"Permission refusée : '{required_permission}' requise."
            )
        return current_user
    return permission_checker


###########################################
##               ROUTES                  ##
###########################################

######## RECEVOIR LE TOKEN ##

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # On normalise l'entrée utilisateur en minuscules pour l'email
    identifier = form_data.username.lower()

    # Recherche flexible : login exact OU email en minuscules
    user = db.query(User).filter(
        or_(
            User.user_login == form_data.username, # Login souvent sensible à la casse
            func.lower(User.email) == identifier   # Email insensible à la casse
        )
    ).first()
    
    if not user or not verify_password(form_data.password, user.user_mdp):
        # On renvoie 401 si l'utilisateur n'existe pas OU si le mdp est faux
        raise HTTPException(
            status_code=401, 
            detail="Identifiant ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_roles = [r.role_name for r in user.roles]
    access_token = create_access_token(data={"sub": str(user.user_id), "roles": user_roles})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "roles": user_roles
    }
    
######## GET ##

@app.get("/search/tracks", response_model=List[schema.TrackView])
def search_tracks(
    query: str, 
    db: Session = Depends(get_db), 
    token: Optional[str] = Depends(optional_oauth2_scheme)
):
    results = db.query(ViewTrackMaterialise).filter(
        or_(
            ViewTrackMaterialise.track_title.ilike(f"%{query}%"),
            ViewTrackMaterialise.artist_name.ilike(f"%{query}%")
        )
    ).limit(50).all()

    if token:
        try:
            # On décode le token pour identifier l'utilisateur
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            
            if user_id:
                # On crée l'entrée dans l'historique
                new_history = SearchHistory(
                    user_id=int(user_id),
                    history_query=query
                )
                db.add(new_history)
                db.commit()
        except Exception as e:
            print(f"Token invalide pour l'historique : {e}")

    return results

@app.get("/artist") 
def get_all_artists(limit: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Artist)
    
    if limit is not None:
        query = query.limit(limit)
    
    return query.all()

@app.get("/artist/{artist_id}", response_model=schema.ArtistDetailed) # Retrait de List[]
def get_one_artist(artist_id: int, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.artist_id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist

@app.get("/topArtist", response_model=List[schema.ArtistDetailed])
def get_top_artists(limit: Optional[int] = 20, db: Session = Depends(get_db)):
    query = db.query(
        Artist.artist_id,
        Artist.artist_name,
        Artist.artist_bio,
        Artist.artist_image_file,
        Artist.artist_location,
        func.sum(Album.album_listens).label("artist_listens")
    ).join(
        ArtistAlbumTrack, Artist.artist_id == ArtistAlbumTrack.artist_id
    ).join(
        Album, ArtistAlbumTrack.album_id == Album.album_id
    ).group_by(
        Artist.artist_id,
        Artist.artist_name,
        Artist.artist_bio,
        Artist.artist_image_file,
        Artist.artist_location
    ).order_by(
        func.sum(Album.album_listens).desc()
    ).limit(limit).all()

    return query

@app.get("/artist/{artist_id}/tracks", response_model=List[schema.TrackView])
def get_artist_tracks(artist_id: int, db: Session = Depends(get_db)):
    # On va chercher dans la View_Track_Materialise pour avoir toutes les infos
    # ou on fait la jointure manuelle
    tracks = db.query(ViewTrackMaterialise).filter(
        ViewTrackMaterialise.artist_id == artist_id
    ).order_by(ViewTrackMaterialise.track_listens.desc()).limit(10).all()
    
    return tracks

@app.get("/album", response_model=List[schema.AlbumDetailed]) 
def get_all_albums(limit: Optional[int] = None, db: Session = Depends(get_db)):
    from sqlalchemy import func

    # Sous-requête : artiste principal de chaque album (le premier par artist_id)
    artist_subq = (
        db.query(
            ArtistAlbumTrack.album_id,
            Artist.artist_name
        )
        .join(Artist, Artist.artist_id == ArtistAlbumTrack.artist_id)
        .distinct(ArtistAlbumTrack.album_id)
        .subquery()
    )

    # Sous-requête : nombre de pistes par album
    track_count_subq = (
        db.query(
            ArtistAlbumTrack.album_id,
            func.count(ArtistAlbumTrack.track_id).label("track_count")
        )
        .group_by(ArtistAlbumTrack.album_id)
        .subquery()
    )

    query = (
        db.query(
            Album,
            artist_subq.c.artist_name,
            track_count_subq.c.track_count
        )
        .outerjoin(artist_subq, Album.album_id == artist_subq.c.album_id)
        .outerjoin(track_count_subq, Album.album_id == track_count_subq.c.album_id)
        .order_by(Album.album_listens.desc())
    )


    if limit is not None:
        query = query.limit(limit)

    results = []
    for album, artist_name, track_count in query.all():
        results.append(schema.AlbumDetailed(
            album_id=album.album_id,
            album_title=album.album_title,
            album_handle=album.album_handle,
            album_information=album.album_information,
            album_date_released=album.album_date_released,
            album_listens=album.album_listens,
            album_favorites=album.album_favorites,
            album_producer=album.album_producer,
            album_image_file=album.album_image_file,
            artist_name=artist_name,
            track_count=track_count or 0
        ))
    return results


@app.get("/topAlbum", response_model=List[schema.Album]) 
def get_top_albums(limit: Optional[int] = 20, db: Session = Depends(get_db)):

    # On sélectionne les colonnes de l'album ET le nom de l'artiste
    query = db.query(
        Album.album_id,
        Album.album_title,
        Album.album_listens,
        Album.album_image_file,
        
        func.min(Artist.artist_name).label("artist_name") 
    ).join(
        ArtistAlbumTrack, Album.album_id == ArtistAlbumTrack.album_id
    ).join(
        Artist, Artist.artist_id == ArtistAlbumTrack.artist_id
    ).group_by(
        Album.album_id,
        Album.album_title,
        Album.album_listens,
        Album.album_image_file
    ).order_by(
        Album.album_listens.desc()
    ).limit(limit).all()

    return query

@app.get("/album/{album_id}", response_model=schema.AlbumDetailed) 
def get_one_album(album_id: int, db: Session = Depends(get_db)):
    # On récupère les infos de l'album et le nom du premier artiste trouvé pour cet album
    # Note: On utilise ArtistAlbumTrack pour le lien
    
    album = db.query(Album).filter(Album.album_id == album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album non trouvé")

    # On cherche l'artiste principal (le premier dans la table de liaison)
    artist_data = db.query(Artist.artist_name).join(
        ArtistAlbumTrack, Artist.artist_id == ArtistAlbumTrack.artist_id
    ).filter(ArtistAlbumTrack.album_id == album_id).first()
    
    artist_name = artist_data[0] if artist_data else "Artiste inconnu"
    
    # On compte les pistes
    track_count = db.query(func.count(ArtistAlbumTrack.track_id)).filter(
        ArtistAlbumTrack.album_id == album_id
    ).scalar()

    return schema.AlbumDetailed(
        album_id=album.album_id,
        album_title=album.album_title,
        album_handle=album.album_handle,
        album_information=album.album_information,
        album_date_released=album.album_date_released,
        album_listens=album.album_listens,
        album_favorites=album.album_favorites,
        album_producer=album.album_producer,
        album_image_file=album.album_image_file,
        artist_name=artist_name,
        track_count=track_count or 0
    )

@app.get("/album/{album_id}/tracks", response_model=List[schema.TrackView])
def get_album_tracks(album_id: int, db: Session = Depends(get_db)):
    # On utilise la vue matérialisée car elle contient déjà album_id
    tracks = db.query(ViewTrackMaterialise).filter(
        ViewTrackMaterialise.album_id == album_id
    ).all()
    
    return tracks


@app.get("/track", response_model=List[schema.Track]) 
def get_tracks(limit: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Track)
    
    if limit is not None:
        query = query.limit(limit)
    
    return query.all()

@app.get("/topTrack", response_model=List[schema.TrackView])
def get_top_tracks(limit: Optional[int] = 20, db: Session = Depends(get_db)):

    try:
        query = db.query(ViewTrackMaterialise).order_by(
            ViewTrackMaterialise.track_listens.desc()
        )
        
        if limit is not None:
            query = query.limit(limit)

        results = query.all()

        if not results:
            return []

        return results
    
    except Exception as e:
        print(f"ERREUR SQL : {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/playlist", response_model=List[schema.Playlist]) 
def get_all_playlists(limit: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Playlist).order_by(Playlist.playlist_listens.desc())
    if limit is not None:
        query = query.limit(limit)
    return query.all()

@app.get("/topPlaylist", response_model=List[schema.Playlist]) 
def get_top_playlists(limit: int = 20, db: Session = Depends(get_db)):

    playlists = db.query(Playlist).group_by(
        Playlist.playlist_id
    ).order_by(
        Playlist.playlist_listens.desc()
    ).limit(limit).all()

    return playlists


@app.get("/users/{user_id}/playlists", response_model=List[schema.Playlist])
def get_user_playlists(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != current_user.user_id:
         raise HTTPException(status_code=403, detail="Accès non autorisé aux playlists d'un autre utilisateur")
    
    playlists = db.query(Playlist).filter(Playlist.user_id == user_id).all()
    return playlists

@app.get("/playlist/{playlist_id}", response_model=schema.PlaylistDetailed)
def get_one_playlist(playlist_id: int, db: Session = Depends(get_db)):
    # Récupère la playlist et le pseudo du créateur via join
    result = db.query(Playlist, User.pseudo.label("creator_pseudo")).join(
        User, Playlist.user_id == User.user_id
    ).filter(Playlist.playlist_id == playlist_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Playlist non trouvée")
    
    playlist, creator_pseudo = result
    
    return schema.PlaylistDetailed(
        playlist_id=playlist.playlist_id,
        playlist_name=playlist.playlist_name,
        playlist_listens=playlist.playlist_listens,
        user_id=playlist.user_id,
        creator_pseudo=creator_pseudo
    )


@app.get("/playlist/{playlist_id}/tracks", response_model=List[schema.TrackView])
def get_playlist_tracks(playlist_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    playlist = db.query(Playlist).filter(Playlist.playlist_id == playlist_id).first()
    
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist non trouvée")
    
    if playlist.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à cette playlist")
    
    track_ids = db.query(PlaylistTrack.track_id).filter(
        PlaylistTrack.playlist_id == playlist_id
    ).all()
    
    track_ids_list = [tid[0] for tid in track_ids]
    
    if not track_ids_list:
        return []
    tracks = db.query(ViewTrackMaterialise).filter(
        ViewTrackMaterialise.track_id.in_(track_ids_list)
    ).all()
    
    return tracks

@app.delete("/playlist/{playlist_id}/tracks/{track_id}")
def remove_track_from_playlist(playlist_id: int, track_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    playlist = db.query(Playlist).filter(Playlist.playlist_id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist non trouvée")
    if playlist.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez modifier que vos propres playlists")
    
    pt = db.query(PlaylistTrack).filter(
        PlaylistTrack.playlist_id == playlist_id,
        PlaylistTrack.track_id == track_id
    ).first()
    
    if not pt:
        raise HTTPException(status_code=404, detail="Titre non trouvé dans cette playlist")
    
    db.delete(pt)
    db.commit()
    return {"detail": "Titre retiré de la playlist"}

@app.delete("/playlist/{playlist_id}")
def delete_playlist(playlist_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    playlist = db.query(Playlist).filter(Playlist.playlist_id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist non trouvée")
    if playlist.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que vos propres playlists")
    
    # On supprime d'abord les entrées dans PlaylistTrack (si pas de cascade en BDD)
    db.query(PlaylistTrack).filter(PlaylistTrack.playlist_id == playlist_id).delete()
    
    db.delete(playlist)
    db.commit()
    return {"detail": "Playlist supprimée avec succès"}

@app.get("/user")
def get_current_user_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    return user

@app.get("/viewTrack", response_model=List[schema.TrackView]) 
def get_view_tracks(limit: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(ViewTrackMaterialise)
    if limit is not None:
        query = query.limit(limit)
    return query.all()

@app.get("/user/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if user.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez accéder qu'à votre propre compte")
    return user

@app.get("/user/favorites/tracks", response_model=List[schema.TrackView])
def get_user_favorite_tracks(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    fav_ids = db.query(TrackUserFavorite.track_id).filter(
        TrackUserFavorite.user_id == current_user.user_id
    ).all()
    
    list_ids = [fid[0] for fid in fav_ids]

    if not list_ids:
        return []

    tracks = db.query(ViewTrackMaterialise).filter(
        ViewTrackMaterialise.track_id.in_(list_ids)
    ).all()

    return tracks

@app.get("/user/favorites/albums", response_model=List[schema.AlbumDetailed])
def get_user_favorite_albums(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    albums = db.query(
        Album.album_id,
        Album.album_title,
        Album.album_listens,
        Album.album_image_file,
        
        func.min(Artist.artist_name).label("artist_name"),
        
        func.count(ArtistAlbumTrack.track_id).label("track_count")
    ).join(
        UserAlbumFavorite, Album.album_id == UserAlbumFavorite.album_id
    ).join(
        ArtistAlbumTrack, Album.album_id == ArtistAlbumTrack.album_id
    ).join(
        Artist, Artist.artist_id == ArtistAlbumTrack.artist_id
    ).filter(
        UserAlbumFavorite.user_id == current_user.user_id
    ).group_by(
        Album.album_id
    ).all()

    return albums

####### RECOMMANDATIONS IA ##

# Import lazy du recommandeur (évite le chargement si pas utilisé)
_recommender = None

def get_recommender():
    """Charge le recommandeur à la première utilisation"""
    global _recommender
    if _recommender is None:
        try:
            from recommender.gru_model import MusicRecommender
            _recommender = MusicRecommender()
        except Exception as e:
            print(f" Recommandeur non disponible : {e}")
            return None
    return _recommender

@app.get("/users/gru_recommendations")
def get_user_recommendations(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Génère des recommandations musicales personnalisées basées sur l'historique de recherche.
    Utilise un modèle GRU + BERT pour l'analyse sémantique.
    """
    
    # Récupération du recommandeur
    recommender = get_recommender()
    if recommender is None or not recommender.is_ready:
        raise HTTPException(
            status_code=503, 
            detail="Service de recommandation indisponible"
        )
    
    # Récupération des 20 dernières recherches (du plus récent au plus ancien)
    search_results = db.query(SearchHistory.history_query).filter(
        SearchHistory.user_id == current_user.user_id
    ).order_by(
        SearchHistory.history_timestamp.desc()
    ).limit(20).all()
    
    if not search_results:
        raise HTTPException(
            status_code=404, 
            detail="Pas d'historique de recherche pour cet utilisateur"
        )
    
    # Extraction des strings et inversion pour ordre chronologique
    history = [row[0] for row in search_results if row[0]]
    history.reverse()
    
    # Prédiction via le modèle GRU
    track_ids = recommender.predict(history, top_k=limit)
    
    return {"recommended_track_ids": track_ids}

@app.get("/users/gru_recommendations/detailed", response_model=List[schema.TrackView])
def get_user_recommendations_detailed(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Version détaillée : Renvoie les objets Track complets (pour affichage playlist direct).
    """
    
    recommender = get_recommender()
    if recommender is None or not recommender.is_ready:
        raise HTTPException(status_code=503, detail="Service de recommandation indisponible")
    
    search_results = db.query(SearchHistory.history_query).filter(
        SearchHistory.user_id == current_user.user_id
    ).order_by(SearchHistory.history_timestamp.desc()).limit(20).all()
    
    if not search_results:
        # Pas d'historique -> Pas de reco (liste vide)
        return []
    
    history = [row[0] for row in search_results if row[0]]
    history.reverse()
    
    # 2. Prédiction des IDs
    track_ids = recommender.predict(history, top_k=limit)
    
    if not track_ids:
        return []

    # 3. Récupération des objets complets depuis la BDD
    tracks_db = db.query(ViewTrackMaterialise).filter(ViewTrackMaterialise.track_id.in_(track_ids)).all()
    
    # 4. Réordonner selon le score de pertinence (car SQL IN casse l'ordre)
    tracks_dict = {t.track_id: t for t in tracks_db}
    ordered_tracks = [tracks_dict[tid] for tid in track_ids if tid in tracks_dict]
    
    return ordered_tracks


####### RECOMMANDATIONS TF-IDF ##

@app.get("/users/tf-idf_recommendations", response_model=List[schema.TrackView])
def get_user_recommendations_detailed(
    limit: int = 10,
    penalty: float = 0.5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Version détaillée : Renvoie les objets Track complets (pour affichage playlist direct).
    """

    try:
        # 1. Récupération des données pour le moteur de recommandation
        tracks_data = db.query(ViewTrackMaterialise).all()

        data_dict = [
            {column.name: getattr(track, column.name) for column in track.__table__.columns} 
            for track in tracks_data
        ]

        df = pd.DataFrame(data_dict)
        df = df.fillna('')

        from recommender.TF_IDF import ContentRecommender
        rec = ContentRecommender(df)

        # 2. Récupération de l'historique
        user_history_query = db.query(
            UserTrackListening.track_id,
        ).filter(
            UserTrackListening.user_id == current_user.user_id
        ).order_by(UserTrackListening.nb_listening.desc()).first()

        if user_history_query is None:
            return []

        # 3. Calcul des recommandations (renvoie souvent une liste d'IDs)
        recommended_df = rec.recommend(user_history_query.track_id, top_k=limit, same_artist_penalty=penalty)

        if recommended_df.empty:
            return []

        # 4. RÉCUPÉRATION DES OBJETS COMPLETS DEPUIS LA VUE
        ids_to_fetch = recommended_df["track_id"].tolist()

        final_tracks = db.query(ViewTrackMaterialise).filter(
            ViewTrackMaterialise.track_id.in_(ids_to_fetch)
        ).all()

        # 5. Trier pour garder l'ordre de pertinence de l'IA
        tracks_dict = {t.track_id: t for t in final_tracks}

        ordered_tracks = []
        for tid in ids_to_fetch:
            if tid in tracks_dict:
                ordered_tracks.append(tracks_dict[tid])

        return ordered_tracks

    except Exception as e:
        print(f" Recommandeur non disponible : {e}")
        return []

####### POST ##

@app.post("/user", status_code=201)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):

    user_dict = user_data.model_dump()

    user_dict["user_mdp"] = hash_password(user_dict["user_mdp"])

    new_user = User(**user_dict)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post("/playlist", response_model=schema.Playlist, status_code=201)
def create_playlist(playlist_data: PlaylistCreate, db: Session = Depends(get_db), current_user: User = Depends(has_permission("playlist_create"))):
    try:
        playlist_dict = playlist_data.model_dump()
        playlist_dict["user_id"] = current_user.user_id
        
        new_playlist = Playlist(**playlist_dict)
        db.add(new_playlist)
        db.commit()
        db.refresh(new_playlist)

        new_playlist_user = PlaylistUser(user_id=current_user.user_id, playlist_id=new_playlist.playlist_id)
        db.add(new_playlist_user)
        db.commit()
        
        return new_playlist
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur création playlist: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne lors de la création")

@app.post("/listeningHistory", status_code=201)
def create_listening_history(listening_history_data: ListeningHistoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    playlist_dict = listening_history_data.model_dump()
    
    playlist_dict["user_id"] = current_user.user_id

    new_listening_history = ListeningHistory(**playlist_dict)
    
    db.add(new_listening_history)
    db.commit()
    db.refresh(new_listening_history)
    
    return new_listening_history

@app.post("/userAlbumListening", status_code=201)
def create_user_album_listening(user_album_listening_data: UserAlbumListeningCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    user_album_listening_dict = user_album_listening_data.model_dump()
    
    user_album_listening_dict["user_id"] = current_user.user_id
    
    new_user_album_listening = UserAlbumListening(**user_album_listening_dict)
    
    db.add(new_user_album_listening)
    db.commit()
    db.refresh(new_user_album_listening)
    
    return new_user_album_listening

@app.post("/userPlaylistListening", status_code=201)
def create_user_playlist_listening(user_playlist_listening_data: UserPlaylistListeningCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    user_playlist_listening_dict = user_playlist_listening_data.model_dump()
    
    user_playlist_listening_dict["user_id"] = current_user.user_id
    
    new_user_playlist_listening = UserPlaylistListening(**user_playlist_listening_dict)
    
    db.add(new_user_playlist_listening)
    db.commit()
    db.refresh(new_user_playlist_listening)
    
    return new_user_playlist_listening

@app.post("/playlistUserFavorite", status_code=201)
def create_playlist_user_favorite(playlist_user_favorite_data: PlaylistUserFavoriteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    playlist_user_favorite_dict = playlist_user_favorite_data.model_dump()
    
    playlist_user_favorite_dict["user_id"] = current_user.user_id
    
    new_playlist_user_favorite = PlaylistUserFavorite(**playlist_user_favorite_dict)
    
    db.add(new_playlist_user_favorite)
    db.commit()
    db.refresh(new_playlist_user_favorite)
    
    return new_playlist_user_favorite

@app.post("/trackUserFavorite", status_code=201)
def create_track_user_favorite(track_user_favorite_data: TrackUserFavoriteCreate, db: Session = Depends(get_db), current_user: User = Depends(has_permission("track_like"))):
    
    # Vérifie si déjà présent
    existing = db.query(TrackUserFavorite).filter(
        TrackUserFavorite.user_id == current_user.user_id,
        TrackUserFavorite.track_id == track_user_favorite_data.track_id
    ).first()
    
    if existing:
        return existing

    track_user_favorite_dict = track_user_favorite_data.model_dump()
    track_user_favorite_dict["user_id"] = current_user.user_id
    
    new_track_user_favorite = TrackUserFavorite(**track_user_favorite_dict)
    
    db.add(new_track_user_favorite)
    db.commit()
    db.refresh(new_track_user_favorite)
    
    return new_track_user_favorite

@app.delete("/trackUserFavorite/{track_id}", status_code=200)
def delete_track_user_favorite(track_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    favorite = db.query(TrackUserFavorite).filter(
        TrackUserFavorite.user_id == current_user.user_id,
        TrackUserFavorite.track_id == track_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favori non trouvé")
        
    db.delete(favorite)
    db.commit()
    return {"message": "Favori supprimé"}

@app.post("/userArtistFavorite", status_code=201)
def create_user_artist_favorite(user_artist_favorite_data: UserArtistFavoriteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    user_artist_favorite_dict = user_artist_favorite_data.model_dump()
    
    user_artist_favorite_dict["user_id"] = current_user.user_id
    
    new_user_artist_favorite = UserArtistFavorite(**user_artist_favorite_dict)
    
    db.add(new_user_artist_favorite)
    db.commit()
    db.refresh(new_user_artist_favorite)
    
    return new_user_artist_favorite

@app.post("/userAlbumFavorite", status_code=201)
def create_user_album_favorite(user_album_favorite_data: UserAlbumFavoriteCreate, db: Session = Depends(get_db), current_user: User = Depends(has_permission("album_like"))):
    
    # Vérifie si déjà présent
    existing = db.query(UserAlbumFavorite).filter(
        UserAlbumFavorite.user_id == current_user.user_id,
        UserAlbumFavorite.album_id == user_album_favorite_data.album_id
    ).first()
    
    if existing:
        return existing

    user_album_favorite_dict = user_album_favorite_data.model_dump()
    user_album_favorite_dict["user_id"] = current_user.user_id
    
    new_user_album_favorite = UserAlbumFavorite(**user_album_favorite_dict)
    
    db.add(new_user_album_favorite)
    db.commit()
    db.refresh(new_user_album_favorite)
    
    return new_user_album_favorite

@app.delete("/userAlbumFavorite/{album_id}", status_code=200)
def delete_user_album_favorite(album_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    favorite = db.query(UserAlbumFavorite).filter(
        UserAlbumFavorite.user_id == current_user.user_id,
        UserAlbumFavorite.album_id == album_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favori non trouvé")
        
    db.delete(favorite)
    db.commit()
    return {"message": "Favori supprimé"}

@app.post("/playlistUser", status_code=201)
def create_playlist_user(playlist_user_data: PlaylistUserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    playlist_user_dict = playlist_user_data.model_dump()
    
    playlist_user_dict["user_id"] = current_user.user_id
    
    new_playlist_user = PlaylistUser(**playlist_user_dict)
    
    db.add(new_playlist_user)
    db.commit()
    db.refresh(new_playlist_user)
    
    return new_playlist_user

@app.post("/playlistTrack", status_code=201)
def create_playlist_track(playlist_track_data: PlaylistTrackCreate, db: Session = Depends(get_db)):
    # Vérifier si le titre est déjà dans la playlist
    existing = db.query(PlaylistTrack).filter(
        PlaylistTrack.playlist_id == playlist_track_data.playlist_id,
        PlaylistTrack.track_id == playlist_track_data.track_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Ce titre est déjà présent dans la playlist")
    
    new_playlist_track = PlaylistTrack(**playlist_track_data.model_dump())
    
    db.add(new_playlist_track)
    db.commit()
    db.refresh(new_playlist_track)
    
    return new_playlist_track

@app.post("/userTrackListening", status_code=201)
def create_user_track_listening_create(user_track_listening_data: UserTrackListeningCreate, db: Session = Depends(get_db), current_user: UserTrackListening = Depends(get_current_user)):
    
    user_track_listening_dict = user_track_listening_data.model_dump()
    
    user_track_listening_dict["user_id"] = current_user.user_id
    
    new_user_track_listening_create = UserTrackListening(**user_track_listening_dict)
    
    db.add(new_user_track_listening_create)
    db.commit()
    db.refresh(new_user_track_listening_create)
    
    return new_user_track_listening_create

@app.post("/SearchHistory", status_code=201)
def create_search_history(search_history_data: SearchHistoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    search_history_dict = search_history_data.model_dump()
    
    search_history_dict["user_id"] = current_user.user_id
    
    new_search_history_create = SearchHistory(**search_history_dict)
    
    db.add(new_search_history_create)
    db.commit()
    db.refresh(new_search_history_create)
    
    return new_search_history_create


####### PATCH ##

@app.patch("/user/{user_id}")
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    if not verify_password(user_data.current_password, db_user.user_mdp):
        raise HTTPException(status_code=401, detail="Mot de passe actuel incorrect")

    if user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Ce n'est pas votre Profil !")

    update_info = user_data.model_dump(exclude_unset=True, exclude={"current_password"})

    for key, value in update_info.items():
        if key == "new_mdp":
            db_user.user_mdp = hash_password(value)
        else:
            setattr(db_user, key, value)

    db.commit()
    return {"status": "success"}

@app.patch("/playlist/{playlist_id}")
def update_playlist(playlist_id: int, playlist_data: PlaylistUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_playlist = db.query(Playlist).filter(Playlist.playlist_id == playlist_id).first()
    
    if not db_playlist:
        raise HTTPException(status_code=404, detail="Playlist non trouvé")

    if db_playlist.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Ce n'est pas votre playlist !")

    update_info = playlist_data.model_dump(exclude_unset=True)

    for key, value in update_info.items():
        setattr(db_playlist, key, value)

    db.commit()
    return {"status": "success"}

@app.patch("/userTrackListening/{track_id}")
def update_user_track_listening(track_id: int, user_track_listening_data: UserTrackListeningUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_user_track_listening = db.query(UserTrackListening).filter(
        UserTrackListening.user_id == current_user.user_id, 
        UserTrackListening.track_id == track_id
    ).first()
    
    if not db_user_track_listening:
        raise HTTPException(status_code=404, detail="UserTrackListening non trouvé")

    update_info = user_track_listening_data.model_dump(exclude_unset=True)

    for key, value in update_info.items():
        setattr(db_user_track_listening, key, value)

    db.commit()
    return {"status": "success"}

@app.patch("/userAlbumListening/{album_id}")
def update_user_album_listening(album_id: int, user_album_listening_data: UserAlbumListeningUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_user_album_listening = db.query(UserAlbumListening).filter(
        UserAlbumListening.user_id == current_user.user_id, 
        UserAlbumListening.album_id == album_id
    ).first()

    if not db_user_album_listening:
        raise HTTPException(status_code=404, detail="UserAlbumListening non trouvé")

    update_info = user_album_listening_data.model_dump(exclude_unset=True)

    for key, value in update_info.items():
        setattr(db_user_album_listening, key, value)

    db.commit()
    return {"status": "success"}

@app.patch("/userPlaylistListening/{playlist_id}")
def update_user_playlist_listening(playlist_id: int, user_playlist_listening_data: UserPlaylistListeningUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_user_playlist_listening = db.query(UserPlaylistListening).filter(
        UserPlaylistListening.user_id == current_user.user_id, 
        UserPlaylistListening.playlist_id == playlist_id
    ).first()

    if not db_user_playlist_listening:
        raise HTTPException(status_code=404, detail="UserPlaylistListening non trouvé")

    update_info = user_playlist_listening_data.model_dump(exclude_unset=True)

    for key, value in update_info.items():
        setattr(db_user_playlist_listening, key, value)

    db.commit()
    return {"status": "success"}


####### DELETE ##

@app.delete("/user/{user_id}", status_code=200)
def anonymize_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Anonymise les données personnelles d'un utilisateur (RGPD - Droit à l'oubli).
    Les statistiques d'écoute sont conservées de manière anonyme.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    if user.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que votre propre compte")
 
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
def remove_favorite_track(user_id: int, track_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retire une piste des favoris de l'utilisateur."""
    favorite = db.query(TrackUserFavorite).filter(
        TrackUserFavorite.user_id == user_id,
        TrackUserFavorite.track_id == track_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favori non trouvé")
    
    if favorite.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que vos propres favoris")
    
    db.delete(favorite)
    db.commit()
    return {"message": "Titre retiré des favoris"}

@app.delete("/users/{user_id}/favorites/artists/{artist_id}", status_code=200)
def remove_favorite_artist(user_id: int, artist_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retire un artiste des favoris de l'utilisateur."""
    favorite = db.query(UserArtistFavorite).filter(
        UserArtistFavorite.user_id == user_id,
        UserArtistFavorite.artist_id == artist_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favori non trouvé")
    
    if favorite.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que vos propres favoris")
    
    db.delete(favorite)
    db.commit()
    return {"message": "Artiste retiré des favoris"}

@app.delete("/users/{user_id}/favorites/albums/{album_id}", status_code=200)
def remove_favorite_album(user_id: int, album_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retire un album des favoris de l'utilisateur."""
    favorite = db.query(UserAlbumFavorite).filter(
        UserAlbumFavorite.user_id == user_id,
        UserAlbumFavorite.album_id == album_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favori non trouvé")
    
    if favorite.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que vos propres favoris")
    
    db.delete(favorite)
    db.commit()
    return {"message": "Album retiré des favoris"}

@app.delete("/playlists/{playlist_id}", status_code=200)
def delete_playlist(playlist_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Supprime une playlist (et ses liens avec les pistes via CASCADE)."""
    playlist = db.query(Playlist).filter(Playlist.playlist_id == playlist_id).first()
    
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist non trouvée")
    
    is_admin = any(r.role_name == "ADMIN" for r in current_user.roles)
    if not is_admin and playlist.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que vos propres playlists")
    
    db.delete(playlist)
    db.commit()
    return {"message": "Playlist supprimée"}

@app.delete("/playlists/{playlist_id}/tracks/{track_id}", status_code=200)
def remove_track_from_playlist(playlist_id: int, track_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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


stats = {
    "total_requests": 0,
    "avg_response_time": 0.0
}

@app.middleware("http")
async def stats_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    stats["total_requests"] += 1
    stats["avg_response_time"] = (
        (stats["avg_response_time"] * (stats["total_requests"] - 1) + duration)
        / stats["total_requests"]
    )

    return response

@app.get("/stats")
def get_stats():
    return stats
from sqlalchemy.dialects.postgresql import insert

@app.post("/track/{track_id}/listen")
def add_listen(track_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Préparation de l'insertion avec mise à jour en cas de conflit (Upsert)
    stmt = insert(UserTrackListening).values(
        user_id=current_user.user_id,
        track_id=track_id,
        nb_listening=1
    )
    
    # Si le couple (user_id, track_id) existe déjà, on ajoute 1 à nb_listening
    stmt = stmt.on_conflict_do_update(
        index_elements=['user_id', 'track_id'],
        set_=dict(nb_listening=UserTrackListening.nb_listening + 1)
    )
    
    db.execute(stmt)
    db.commit()

    # On rafraîchit la vue matérialisée pour que le +1 soit visible sur le front
    # CONCURRENTLY permet de ne pas bloquer les lectures pendant le rafraîchissement
    db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY sae.view_track_materialise"))
    db.commit()

    return {"status": "success"}

# Route pour l'Album
@app.post("/album/{album_id}/listen")
def add_album_listen(album_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = insert(UserAlbumListening).values(
        user_id=current_user.user_id,
        album_id=album_id,
        nb_listening=1
    )
    
    stmt = stmt.on_conflict_do_update(
        index_elements=['user_id', 'album_id'],
        set_=dict(nb_listening=UserAlbumListening.nb_listening + 1)
    )
    
    db.execute(stmt)
    db.commit()
    
    db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY sae.view_track_materialise"))
    db.commit()
    
    return {"status": "success"}

@app.post("/playlist/{playlist_id}/listen")
def add_playlist_listen(playlist_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = insert(UserPlaylistListening).values(
        user_id=current_user.user_id,
        playlist_id=playlist_id,
        nb_listening=1
    )
    
    stmt = stmt.on_conflict_do_update(
        index_elements=['user_id', 'playlist_id'],
        set_=dict(nb_listening=UserPlaylistListening.nb_listening + 1)
    )
    
    db.execute(stmt)
    db.commit()
    
    db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY sae.view_track_materialise"))
    db.commit()
    
    return {"status": "success"}

@app.get("/track/{track_id}/context")
def get_track_context(track_id: int, db: Session = Depends(get_db)):
    # On cherche l'album lié à ce morceau dans la table de liaison
    # Exemple basé sur ton schéma sae.Artist_Album_Track
    result = db.execute(text("""
        SELECT album_id FROM sae.Artist_Album_Track 
        WHERE track_id = :tid LIMIT 1
    """), {"tid": track_id}).fetchone()
    
    if result:
        return {"album_id": result.album_id}
    return {"album_id": None}

# 1. Top 5 des musiques les plus écoutées par l'utilisateur
@app.get("/stats/user/top-tracks")
def get_top_tracks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = text("""
        SELECT 
            utl.track_id, 
            t.track_title, 
            utl.nb_listening,
            g.genre_title as track_genre -- On récupère le genre ici
        FROM sae.User_Track_Listening utl
        JOIN sae.Track t ON utl.track_id = t.track_id
        -- On joint la table Genre via la table de liaison majoritaire
        LEFT JOIN sae.Track_Genre_Majoritaire tgm ON t.track_id = tgm.track_id
        LEFT JOIN sae.Genre g ON tgm.genre_id = g.genre_id
        WHERE utl.user_id = :uid
          AND t.track_title NOT ILIKE 'Only Instrumental'
        ORDER BY utl.nb_listening DESC
        LIMIT 5
    """)
    result = db.execute(query, {"uid": current_user.user_id}).mappings().all()
    return list(result)


# 3. Compteurs simples (Favoris et Playlists)
@app.get("/stats/user/counts")
def get_user_counts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    favs = db.execute(text("SELECT COUNT(*) FROM sae.Track_User_Favorite WHERE user_id = :uid"), {"uid": current_user.user_id}).scalar()
    playlists = db.execute(text("SELECT COUNT(*) FROM sae.Playlist WHERE user_id = :uid"), {"uid": current_user.user_id}).scalar()
    return {"favoris": favs, "playlists": playlists}

###########################################
##      AUTORISATIONS & LANCEMENT        ##
###########################################

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
