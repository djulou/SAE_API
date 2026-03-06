import { useState, useEffect } from "react"
import CarteChanson from "./carte_chanson"
import "../index.css"


type Artist = {
  track_id: number;
  track_title: string;
  artist_name: string;
  album_image_file: string;
};

type Props = {
  isConnected: boolean;
};

export default function ArtistsFavorites({ isConnected }: Props) {
  const [favorites, setFavorites] = useState<Artist[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchFavorites() {
      const token = localStorage.getItem("token");
      if (!token) return;

      try {
        const response = await fetch("http://127.0.0.1:8000/user/favorites/tracks", {
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
    }
  }, [isConnected]);

  if (!isConnected) {
    return <p>Veuillez vous connecter pour voir vos favoris.</p>;
  }

  return (
    <div className="favorites-page">
      <h1>Mes Titres Aimés</h1>

      {loading ? (
        <p>Chargement...</p>
      ) : favorites.length > 0 ? (
        <div className="tracks-grid">
          {favorites.map((track) => (
            <CarteChanson
              key={`fav-${track.track_id}`}
              trackId={track.track_id}
              title={track.track_title}
              artist={track.artist_name}
              pochette={track.album_image_file}
              isConnected={isConnected}
              // Si vous voulez ajouter une fonction pour supprimer des favoris plus tard :
              // onRemove={() => handleRemove(track.track_id)}
            />
          ))}
        </div>
      ) : (
        <p>Vous n'avez pas encore de titres favoris.</p>
      )}
    </div>
  );
}