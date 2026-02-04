from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from models import (
    Album, User, Playlist, Track,
    UserCreate, PlaylistCreate
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
    "password": "postgres",
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
