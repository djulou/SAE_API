from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from models import Album

import uvicorn
import os

app = FastAPI()

# Configuration BDD
db_host = os.getenv("DB_HOST", "localhost")
DATABASE_URL = "postgresql://postgres:@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)
       
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.get("/album") 
def get_all_albums(db: Session = Depends(get_db)):
    return db.query(Album).all()

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
