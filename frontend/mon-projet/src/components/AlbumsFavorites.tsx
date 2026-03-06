import { useState, useEffect } from "react"
import CarteAlbum from "./carte_album"
import NavBarSide from "./NavBarSide"
import AddToPlaylistModal from "./AddToPlaylistModal"


import type { Page } from "../types/Page"
import type { Album } from "../types/Album"

import "../index.css"



interface PlaylistDB {
  playlist_id: number;
  playlist_name: string;
  playlist_listens: number;
  user_id: number;
}

type Props = {
  isConnected: boolean
  onNavigate: (page: Page) => void
  onOpenPlaylist: (id: number) => void
  userId: number | null;
};

export default function AlbumsFavorites({ isConnected, onNavigate, onOpenPlaylist, userId }: Props) {
  const [favorites, setFavorites] = useState<Album[]>([]);
  const [loading, setLoading] = useState(true);
  const [userPlaylists, setUserPlaylists] = useState<PlaylistDB[]>([]);

  const [modalOpen, setModalOpen] = useState(false)
  const [selectedAlbumId, setSelectedAlbumId] = useState<number | null>(null)

  const handleAddAlbum = (trackId: number) => {
    setSelectedAlbumId(trackId)
    setModalOpen(true)
  }

  useEffect(() => {

    async function loadUserPlaylists() {
      if (!isConnected || !userId) return;
      try {
        const token = localStorage.getItem("token");
        if (token) {
          const res = await fetch(`http://127.0.0.1:8000/users/${userId}/playlists`, {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
          });
          if (res.ok) {
            setUserPlaylists(await res.json());
          }
        }
      } catch (e) {
        console.error("Erreur lors de la récupération des playlists :", e);
      }
    }

    async function fetchFavorites() {
      const token = localStorage.getItem("token");
      if (!token) return;

      try {
        const response = await fetch("http://127.0.0.1:8000/user/favorites/albums", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          setFavorites(data);
        }
      } catch (error) {
        console.error("Erreur chargement favoris:", error);
      } finally {
        setLoading(false);
      }
    }

    if (isConnected) {
      fetchFavorites();
      loadUserPlaylists();
    }
  }, [isConnected, userId]);

  if (!isConnected) {
    return <p>Veuillez vous connecter pour voir vos favoris.</p>;
  }

  return (

    <div className="accueil-layout">
    <NavBarSide 
        onNavigate={onNavigate}
        isConnected={isConnected}
        setModalOpen={setModalOpen}
        onOpenPlaylist={onOpenPlaylist}
        setSelectedTrackId={setSelectedAlbumId}
        userPlaylists={userPlaylists}
    />

    <div className="favorites-page accueil-content">
      <h1>Mes albums Aimés</h1>

      {loading ? (
        <p>Chargement...</p>
      ) : favorites.length > 0 ? (
        <div className="tracks-grid">
          {favorites.map((album) => (
            <CarteAlbum
                  title={album.album_title}
                  artist={album.artist_name}
                  pochette={album.album_image_file}
                  isConnected={isConnected}
                  onAdd={() => handleAddAlbum(album.album_id)}
                />
          ))}
        </div>
      ) : (
        <p>Vous n'avez pas encore d'albums favoris.</p>
      )}
    </div>
    {/* Le Modal est rendu ici */}
    <AddToPlaylistModal
    isOpen={modalOpen}
    onClose={() => setModalOpen(false)}
    trackId={selectedAlbumId}
    userId={userId}
    />
    </div>
  );
}