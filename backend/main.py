from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

import bcrypt

from models import ( 
    Album, User, Playlist, Track, ListeningHistory, UserAlbumListening, UserPlaylistListening,
    PlaylistUserFavorite, TrackUserFavorite, UserArtistFavorite, UserAlbumFavorite, PlaylistUser,
    PlaylistTrack
)

from schema import (    
    UserCreate, PlaylistCreate, ListeningHistoryCreate, UserAlbumListeningCreate, UserPlaylistListeningCreate,
    PlaylistUserFavoriteCreate, TrackUserFavoriteCreate, UserArtistFavoriteCreate, UserAlbumFavoriteCreate, PlaylistUserCreate,
    PlaylistTrackCreate,

    UserUpdate, PlaylistUpdate
)

import uvicorn
import os
from datetime import date, datetime, timedelta
from dotenv import load_dotenv

from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

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
def get_user_by_email(email: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    if user.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez accéder qu'à votre propre compte")
    
    return user

@app.get("/user/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    if user.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez accéder qu'à votre propre compte")
    
    return user

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

@app.post("/playlist", status_code=201)
def create_playlist(playlist_data: PlaylistCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    playlist_dict = playlist_data.model_dump()

    playlist_dict["user_id"] = current_user.user_id
    
    new_playlist = Playlist(**playlist_dict)
    
    db.add(new_playlist)
    db.commit()
    db.refresh(new_playlist)
    
    return new_playlist

@app.post("/listeningHistory", status_code=201)
def create_listening_history(listening_history_data: ListeningHistoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    playlist_dict = listening_history_data.model_dump()
    
    playlist_dict["user_id"] = current_user.user_id

    new_listening_history = ListeningHistory(**playlist_dict)
    
    db.add(new_listening_history)
    db.commit()
    db.refresh(new_listening_history)
    
    return new_listening_history

@app.post("/UserAlbumListening", status_code=201)
def create_user_album_listening(user_album_listening_data: UserAlbumListeningCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    user_album_listening_dict = user_album_listening_data.model_dump()
    
    user_album_listening_dict["user_id"] = current_user.user_id
    
    new_user_album_listening = UserAlbumListening(**user_album_listening_dict)
    
    db.add(new_user_album_listening)
    db.commit()
    db.refresh(new_user_album_listening)
    
    return new_user_album_listening

@app.post("/UserPlaylistListening", status_code=201)
def create_user_playlist_listening(user_playlist_listening_data: UserPlaylistListeningCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    user_playlist_listening_dict = user_playlist_listening_data.model_dump()
    
    user_playlist_listening_dict["user_id"] = current_user.user_id
    
    new_user_playlist_listening = UserPlaylistListening(**user_playlist_listening_dict)
    
    db.add(new_user_playlist_listening)
    db.commit()
    db.refresh(new_user_playlist_listening)
    
    return new_user_playlist_listening

@app.post("/PlaylistUserFavorite", status_code=201)
def create_playlist_user_favorite(playlist_user_favorite_data: PlaylistUserFavoriteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    playlist_user_favorite_dict = playlist_user_favorite_data.model_dump()
    
    playlist_user_favorite_dict["user_id"] = current_user.user_id
    
    new_playlist_user_favorite = PlaylistUserFavorite(**playlist_user_favorite_dict)
    
    db.add(new_playlist_user_favorite)
    db.commit()
    db.refresh(new_playlist_user_favorite)
    
    return new_playlist_user_favorite

@app.post("/TrackUserFavorite", status_code=201)
def create_track_user_favorite(track_user_favorite_data: TrackUserFavoriteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    track_user_favorite_dict = track_user_favorite_data.model_dump()
    
    track_user_favorite_dict["user_id"] = current_user.user_id
    
    new_track_user_favorite = TrackUserFavorite(**track_user_favorite_dict)
    
    db.add(new_track_user_favorite)
    db.commit()
    db.refresh(new_track_user_favorite)
    
    return new_track_user_favorite

@app.post("/UserArtistFavorite", status_code=201)
def create_user_artist_favorite(user_artist_favorite_data: UserArtistFavoriteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    user_artist_favorite_dict = user_artist_favorite_data.model_dump()
    
    user_artist_favorite_dict["user_id"] = current_user.user_id
    
    new_user_artist_favorite = UserArtistFavorite(**user_artist_favorite_dict)
    
    db.add(new_user_artist_favorite)
    db.commit()
    db.refresh(new_user_artist_favorite)
    
    return new_user_artist_favorite

@app.post("/UserAlbumFavorite", status_code=201)
def create_user_album_favorite(user_album_favorite_data: UserAlbumFavoriteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    user_album_favorite_dict = user_album_favorite_data.model_dump()
    
    user_album_favorite_dict["user_id"] = current_user.user_id
    
    new_user_album_favorite = UserAlbumFavorite(**user_album_favorite_dict)
    
    db.add(new_user_album_favorite)
    db.commit()
    db.refresh(new_user_album_favorite)
    
    return new_user_album_favorite

@app.post("/PlaylistUser", status_code=201)
def create_playlist_user(playlist_user_data: PlaylistUserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    playlist_user_dict = playlist_user_data.model_dump()
    
    playlist_user_dict["user_id"] = current_user.user_id
    
    new_playlist_user = PlaylistUser(**playlist_user_dict)
    
    db.add(new_playlist_user)
    db.commit()
    db.refresh(new_playlist_user)
    
    return new_playlist_user

@app.post("/PlaylistTrack", status_code=201)
def create_playlist_track(playlist_track_data: PlaylistTrackCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    new_playlist_track = PlaylistTrack(**playlist_track_data.model_dump())
    
    db.add(new_playlist_track)
    db.commit()
    db.refresh(new_playlist_track)
    
    return new_playlist_track


####### PATCH ##

@app.patch("/user/{user_id}")
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    if not verify_password(user_data.current_password, db_user.user_mdp):
        raise HTTPException(status_code=401, detail="Mot de passe actuel incorrect")

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
