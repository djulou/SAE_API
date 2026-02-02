import { useState, useEffect } from "react";

import type { Album } from "./models/models";
import "./App.css";

function App() {
  const [albums, setAlbums] = useState<Album[]>([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/album")
      .then((res) => res.json())
      .then((data) => setAlbums(data));
  }, []);

  return (
    <>
      <div className="App">
        <h1>Ma Collection d'Albums</h1>
        <div className="album-list">
          {albums.length > 0 ? (
            albums.map((item, index) => (
              <div key={index} className="album-card">
                {/* Adapte les noms (item.title, item.artist) selon ta base SQL */}
                <h3>{item.album_title || "Titre inconnu"}</h3>
              </div>
            ))
          ) : (
            <p>Chargement des albums...</p>
          )}
        </div>
      </div>
    </>
  );
}

export default App;
