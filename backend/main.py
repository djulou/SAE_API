from fastapi import FastAPI, Depends, HTTPException
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

import bcrypt

from models import ( 
    Album, User, Playlist, Track, Artist, ListeningHistory, UserAlbumListening, UserPlaylistListening,
    PlaylistUserFavorite, TrackUserFavorite, UserArtistFavorite, UserAlbumFavorite, PlaylistUser,
    PlaylistTrack, UserTrackListening, SearchHistory, ViewTrackMaterialise
)

import schema

from schema import (    
    UserCreate, PlaylistCreate, ListeningHistoryCreate, UserAlbumListeningCreate, UserPlaylistListeningCreate,
    PlaylistUserFavoriteCreate, TrackUserFavoriteCreate, UserArtistFavoriteCreate, UserAlbumFavoriteCreate, PlaylistUserCreate,
    PlaylistTrackCreate, UserTrackListeningCreate, SearchHistoryCreate, TrackView,

    UserUpdate, PlaylistUpdate, UserTrackListeningUpdate, UserAlbumListeningUpdate, UserPlaylistListeningUpdate
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


###########################################
##             CONFIGURATION             ##
###########################################

app = FastAPI()

# Configuration BDD
db_host = os.getenv("DB_HOST", "localhost")
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "admin",
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
        user_login: str = payload.get("sub")
        if user_login is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.user_login == user_login).first()
    if user is None:
        raise credentials_exception
    return user


###########################################
##               ROUTES                  ##
###########################################

######## RECEVOIR LE TOKEN ##

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_login == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.user_mdp):
        raise HTTPException(status_code=401, detail="Login ou mot de passe incorrect")

    # Générer le token
    access_token = create_access_token(data={"sub": user.user_login})
    
    return {"access_token": access_token, "token_type": "bearer"}


######## GET ##

@app.get("/artist") 
def get_all_artists(limit: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Artist)
    
    if limit is not None:
        query = query.limit(limit)
    
    return query.all()

@app.get("/artist/{artist_id}", response_model=List[schema.Artist]) 
def get_one_artist(artist_id: int, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.artist_id == artist_id).first()
    
    if artist is None:
        raise HTTPException(status_code=404, detail="Album non trouvé")
        
    return artist

@app.get("/album") 
def get_all_albums(limit: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Album)
    
    if limit is not None:
        query = query.limit(limit)
    
    return query.all()

@app.get("/album/{album_id}", response_model=List[schema.Album]) 
def get_one_album(album_id: int, db: Session = Depends(get_db)):
    album = db.query(Album).filter(Album.album_id == album_id).first()
    
    if album is None:
        raise HTTPException(status_code=404, detail="Album non trouvé")
        
    return album

@app.get("/track", response_model=List[schema.Track]) 
def get_tracks(limit: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Track)
    
    if limit is not None:
        query = query.limit(limit)
    
    return query.all()

@app.get("/playlist") 
def get_all_playlists(db: Session = Depends(get_db)):
    return db.query(Playlist).all()

@app.get("/users/{user_id}/playlists", response_model=List[schema.Playlist])
def get_user_playlists(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != current_user.user_id:
         raise HTTPException(status_code=403, detail="Accès non autorisé aux playlists d'un autre utilisateur")
    
    playlists = db.query(Playlist).filter(Playlist.user_id == user_id).all()
    return playlists

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

@app.get("/user")
def get_current_user_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return current_user

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
def create_playlist(playlist_data: PlaylistCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
def create_track_user_favorite(track_user_favorite_data: TrackUserFavoriteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
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
def create_user_album_favorite(user_album_favorite_data: UserAlbumFavoriteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    user_album_favorite_dict = user_album_favorite_data.model_dump()
    
    user_album_favorite_dict["user_id"] = current_user.user_id
    
    new_user_album_favorite = UserAlbumFavorite(**user_album_favorite_dict)
    
    db.add(new_user_album_favorite)
    db.commit()
    db.refresh(new_user_album_favorite)
    
    return new_user_album_favorite

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
    
    if playlist.user_id != current_user.user_id:
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
