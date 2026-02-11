import { useState, useEffect } from "react"
import Carousel from "./components/Carousel"
import CarteChanson from "./components/carte_chanson"
import CartePlaylist from "./components/carte_playlist"
import CarteAlbum from "./components/carte_album"
import { getChansons } from "./services/chansonService"
import type { Playlist } from "./types/Playlist"
import type { Album } from "./types/Album"
import viteLogo from "/vite.svg"

type AccueilProps = {
  isConnected: boolean
}

interface Track {
  track_id: number;
  track_title: string;
  artist_name: string;
  album_image_file: string;
}
 
export default function Accueil( {isConnected = false} : AccueilProps)  {
  
  const [tracks, setTracks] = useState<Track[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTracks() {
      try {
        const response = await fetch("http://127.0.0.1:8000/viewTrack?limit=100");
        const data = await response.json();
        setTracks(data);
      } catch (error) {
        console.error("Erreur :", error);
      } finally {
        setLoading(false);
      }
    }

    loadTracks();
  }, []);

  const playlists: Playlist[] = Array.from({ length: 50 }, () => ({
    title: "Top Disney",
    creator: "Orchestra",
    pochette: viteLogo,
  }))

  const albums: Album[] = Array.from({ length: 5 }, () => ({
    title: "Frozen",
    artist: "Idina Menzel",
    pochette: viteLogo,
  }))

  /* 🔎 Filtres */
  const playlistsFiltrees = playlists
  

  const albumsFiltres = albums
  

  return (
    <>

      <div className="accueil-layout">
        <nav className="menu-favoris">
            <ul className="list-aime">
                <li>Écouté récemment</li>
                <li>Titres aimés</li>
                <li>Albums</li>
                <li>Artistes</li>
            </ul>

            <button className="btn-add-playlist">
                Ajouter une Playlist
            </button>

          <ul className="list-playlist"></ul>
        </nav>
      <main className="accueil-content">


      <h2>Musiques recommandées</h2>
      {loading ? (
        <p>Chargement des musiques...</p>
      ) : (
        <Carousel>
          {tracks.map((track) => (
            <CarteChanson
              key={track.track_id}
              title={track.track_title}
              artist={track.artist_name}
              // artist={track.artists.map(a => a.artist_name).join(", ")}
              pochette={track.album_image_file}
              isConnected={isConnected}
            />
          ))}
        </Carousel>
      )}

      <h2>Playlists recommandées</h2>
      <Carousel>
        {playlistsFiltrees.map((playlist, index) => (
          <CartePlaylist
            key={index}
            title={playlist.title}
            creator={playlist.creator}
            pochette={playlist.pochette}
            isConnected={isConnected}
          />
        ))}
      </Carousel>

      <h2>Albums recommandés</h2>
      <Carousel>
        {albumsFiltres.map((album, index) => (
          <CarteAlbum
            key={index}
            title={album.title}
            artist={album.artist}
            pochette={album.pochette}
            isConnected={isConnected}
          />
        ))}
      </Carousel>
    </main>
    </div>
    </>
  )
}