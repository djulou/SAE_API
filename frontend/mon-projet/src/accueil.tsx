import { useState, useEffect } from "react"
import Carousel from "./components/Carousel"
import CarteChanson from "./components/carte_chanson"
import CartePlaylist from "./components/carte_playlist"
import CarteAlbum from "./components/carte_album"
import AddToPlaylistModal from "./components/AddToPlaylistModal" // Import du modal
import { getChansons } from "./services/chansonService"
import type { Playlist } from "./types/Playlist"
import type { Album } from "./types/Album"
import viteLogo from "/vite.svg"

type AccueilProps = {
  isConnected: boolean
  userId: number | null
}

interface Track {
  track_id: number;
  track_title: string;
  artist_name: string;
  album_image_file: string;
}
 
export default function Accueil( {isConnected = false} : AccueilProps)  {
  
  const [tracks, setTracks] = useState<Track[]>([]);
  const [recoTracks, setRecoTracks] = useState<Track[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        // 1. Chargement des musiques générales (Public)
        const resTracks = await fetch("http://127.0.0.1:8000/viewTrack?limit=100");
        const dataTracks = await resTracks.json();
        setTracks(dataTracks);

        // 2. Chargement des recommandations (Privé - seulement si connecté)
        if (isConnected) {
          const token = localStorage.getItem("token"); // Récupération du token
          
          if (token) {
            const resReco = await fetch("http://127.0.0.1:8000/users/gru_recommendations/detailed?limit=10", {
              method: "GET",
              headers: {
                "Authorization": `Bearer ${token}`, // Envoi du badge d'accès
                "Content-Type": "application/json"
              }
            });

            if (resReco.ok) {
              const dataReco = await resReco.json();
              setRecoTracks(dataReco);
            }
          }
        }
      } catch (error) {
        console.error("Erreur lors du chargement :", error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [isConnected]);

  // État pour la gestion du modal
  const [modalOpen, setModalOpen] = useState(false)
  const [selectedTrackId, setSelectedTrackId] = useState<number | null>(null)
  const playlists: Partial<Playlist>[] = Array.from({ length: 50 }, () => ({
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


  const handleAddTrack = (trackId: number) => {
    setSelectedTrackId(trackId)
    setModalOpen(true)
  }

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

      <h2>Selon vos recherches</h2>
      {isConnected && recoTracks.length > 0 && (
        <>
          <h2>Selon vos recherches</h2>
          <Carousel>
            {recoTracks.map((track) => (
              <CarteChanson
                key={`reco-${track.track_id}`}
                title={track.track_title}
                artist={track.artist_name}
                pochette={track.album_image_file || viteLogo}
                isConnected={isConnected}
              />
            ))}
          </Carousel>
        </>
      )}

          <h2>Playlists recommandées</h2>
          <Carousel>
            {playlistsFiltrees.map((playlist, index) => (
              <CartePlaylist
                key={index}
                title={playlist.title || playlist.playlist_name || "Sans titre"}
                creator={playlist.creator || "Inconnu"}
                pochette={playlist.pochette || viteLogo}
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

      {/* Le Modal est rendu ici */}
      <AddToPlaylistModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        trackId={selectedTrackId}
        userId={userId}
      />
    </>
  )
}