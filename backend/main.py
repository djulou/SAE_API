from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from models import (
    Album, User, Playlist, Track, ListeningHistory, UserAlbumListening, UserPlaylistListening,
    PlaylistUserFavorite, TrackUserFavorite, UserArtistFavorite, UserAlbumFavorite, PlaylistUser,
    PlaylistTrack,
    
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
    user = db.query(User).filter(User.user_email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return user


####### POST ##

@app.post("/user", status_code=201)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    new_user = User(**user_data.dict())
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post("/playlist", status_code=201)
def create_playlist(playlist_data: PlaylistCreate, db: Session = Depends(get_db)):
    new_playlist = Playlist(**playlist_data.dict())
    
    db.add(new_playlist)
    db.commit()
    db.refresh(new_playlist)
    
    return new_playlist

@app.post("/listeningHistory", status_code=201)
def create_listening_history(listening_history_data: ListeningHistoryCreate, db: Session = Depends(get_db)):
    new_listening_history = ListeningHistory(**listening_history_data.dict())
    
    db.add(new_listening_history)
    db.commit()
    db.refresh(new_listening_history)
    
    return new_listening_history

@app.post("/UserAlbumListening", status_code=201)
def create_user_album_listening(user_album_listening_data: UserAlbumListeningCreate, db: Session = Depends(get_db)):
    new_user_album_listening = UserAlbumListening(**user_album_listening_data.dict())
    
    db.add(new_user_album_listening)
    db.commit()
    db.refresh(new_user_album_listening)
    
    return new_user_album_listening

@app.post("/UserPlaylistListening", status_code=201)
def create_user_playlist_listening(user_album_listening_data: UserPlaylistListeningCreate, db: Session = Depends(get_db)):
    new_user_playlist_listening = UserPlaylistListening(**user_album_listening_data.dict())
    
    db.add(new_user_playlist_listening)
    db.commit()
    db.refresh(new_user_playlist_listening)
    
    return new_user_playlist_listening

@app.post("/PlaylistUserFavorite", status_code=201)
def create_playlist_user_favorite(playlist_user_favorite_data: PlaylistUserFavoriteCreate, db: Session = Depends(get_db)):
    new_playlist_user_favorite = PlaylistUserFavorite(**playlist_user_favorite_data.dict())
    
    db.add(new_playlist_user_favorite)
    db.commit()
    db.refresh(new_playlist_user_favorite)
    
    return new_playlist_user_favorite

@app.post("/TrackUserFavorite", status_code=201)
def create_track_user_favorite(track_user_favorite_data: TrackUserFavoriteCreate, db: Session = Depends(get_db)):
    new_track_user_favorite = TrackUserFavorite(**track_user_favorite_data.dict())
    
    db.add(new_track_user_favorite)
    db.commit()
    db.refresh(new_track_user_favorite)
    
    return new_track_user_favorite

@app.post("/UserArtistFavorite", status_code=201)
def create_user_artist_favorite(user_artist_favorite_data: UserArtistFavoriteCreate, db: Session = Depends(get_db)):
    new_user_artist_favorite = UserArtistFavorite(**user_artist_favorite_data.dict())
    
    db.add(new_user_artist_favorite)
    db.commit()
    db.refresh(new_user_artist_favorite)
    
    return new_user_artist_favorite

@app.post("/UserAlbumFavorite", status_code=201)
def create_user_album_favorite(user_album_favorite_data: UserAlbumFavoriteCreate, db: Session = Depends(get_db)):
    new_user_album_favorite = UserAlbumFavorite(**user_album_favorite_data.dict())
    
    db.add(new_user_album_favorite)
    db.commit()
    db.refresh(new_user_album_favorite)
    
    return new_user_album_favorite

@app.post("/PlaylistUser", status_code=201)
def create_playlist_user(playlist_user_data: PlaylistUserCreate, db: Session = Depends(get_db)):
    new_playlist_user = PlaylistUser(**playlist_user_data.dict())
    
    db.add(new_playlist_user)
    db.commit()
    db.refresh(new_playlist_user)
    
    return new_playlist_user

@app.post("/PlaylistTrack", status_code=201)
def create_playlist_track(playlist_track_data: PlaylistTrackCreate, db: Session = Depends(get_db)):
    new_playlist_track = PlaylistTrack(**playlist_track_data.dict())
    
    db.add(new_playlist_track)
    db.commit()
    db.refresh(new_playlist_track)
    
    return new_playlist_track

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
