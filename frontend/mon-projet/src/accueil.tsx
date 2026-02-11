import { useState } from "react"
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


export default function Accueil({ isConnected = false, userId }: AccueilProps) {
  const chansons = getChansons()

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
  const chansonsFiltrees = chansons

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

          <button className="btn-add-playlist" onClick={() => handleAddTrack(null as any)}>
            Ajouter une Playlist
          </button>

          <ul className="list-playlist"></ul>
        </nav>
        <main className="accueil-content">

          <h2>Musiques recommandées</h2>
          <Carousel>
            {chansonsFiltrees.map((chanson, index) => (
              <CarteChanson
                key={index}
                title={chanson.title}
                artist={chanson.artist}
                pochette={chanson.pochette}
                isConnected={isConnected}
                onAdd={() => handleAddTrack(index + 1)} // On simule un ID car getChansons renvoie des mocks sans ID
              />
            ))}
          </Carousel>

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
