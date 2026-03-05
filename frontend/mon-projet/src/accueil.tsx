import { useState, useEffect } from "react";
import Carousel from "./components/Carousel";
import CarteChanson from "./components/carte_chanson";
import CarteArtist from "./components/carte_artist";
import CarteAlbum from "./components/carte_album";
import AddToPlaylistModal from "./components/AddToPlaylistModal";

import { getChansons } from "./services/chansonService";
import type { Playlist } from "./types/Playlist";
import type { Album } from "./types/Album";

//
type AccueilProps = {
  isConnected: boolean;
  userId: number | null;
  onOpenPlaylist: (id: number) => void;
  onOpenAlbum: (id: number) => void;
  onOpenArtist: (id: number) => void;
  searchQuery: string;
};

interface Track {
  track_id: number;
  track_title: string;
  artist_name: string;
  album_image_file: string;
  track_interest?: number;
}

interface PlaylistDB {
  playlist_id: number;
  playlist_name: string;
  playlist_listens: number;
  user_id: number;
}

interface Artist {
  artist_id: number;
  artist_name: string;
  artist_listens: number;
}

export default function Accueil({
  isConnected = false,
  userId,
  onOpenPlaylist,
  onOpenAlbum,
  onOpenArtist,
  searchQuery,
}: AccueilProps) {
  const [tracks, setTracks] = useState<Track[]>([]);
  const [recoGRU, setRecoGRU] = useState<Track[]>([]);
  const [recoTF_IDF, setRecoTF_IDF] = useState<Track[]>([]);
  const [topAlbum, setTopAlbum] = useState<Album[]>([]);
  const [userPlaylists, setUserPlaylists] = useState<PlaylistDB[]>([]);

  const [loadingTrack, setLoadingTrack] = useState(true);
  const [loadingGRU, setLoadingGRU] = useState(false);
  const [loadingTF_IDF, setLoadingTF_IDF] = useState(false);
  const [loadingTopAlbum, setLoadingTopAlbum] = useState(false);
  const [topArtists, setTopArtists] = useState<Artist[]>([]); // Renommé
  const [loadingTopArtist, setLoadingTopArtist] = useState(false); // Renommé

  const [searchResults, setSearchResults] = useState<Track[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function performSearch() {
      if (!searchQuery) {
        setSearchResults([]); // On vide si recherche vide
        setIsSearching(false);
        return;
      }

      setIsSearching(true);

      const token = localStorage.getItem("token");

      const headers: any = {
        "Content-Type": "application/json",
      };

      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      try {
        const response = await fetch(
          `http://127.0.0.1:8000/search/tracks?query=${encodeURIComponent(searchQuery)}`,
          {
            method: "GET",
            headers: headers,
          },
        );

        const data = await response.json();
        setSearchResults(data);
      } catch (error) {
        console.error("Erreur recherche:", error);
      } finally {
        setIsSearching(false);
      }
    }

    async function loadTracks() {
      setError(null);
      try {
        const res = await fetch("http://127.0.0.1:8000/topTrack?limit=100", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (res.ok) {
          const data = await res.json();
          setTracks(data);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoadingTrack(false);
      }
    }

    async function loadGRU() {
      if (!isConnected) return;

      setLoadingGRU(true);
      try {
        const token = localStorage.getItem("token");

        if (token && isConnected) {
          const res = await fetch(
            "http://127.0.0.1:8000/users/gru_recommendations/detailed?limit=10",
            {
              method: "GET",
              headers: {
                Authorization: `Bearer ${token}`, // Envoi du badge d'accès
                "Content-Type": "application/json",
              },
            },
          );

          if (res.ok) {
            const data = await res.json();
            setRecoGRU(data);
          }
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoadingGRU(false);
      }
    }

    async function loadTF_IDF() {
      if (!isConnected) return;

      setLoadingTF_IDF(true);
      try {
        const token = localStorage.getItem("token");

        if (token && isConnected) {
          const res = await fetch(
            "http://127.0.0.1:8000/users/tf-idf_recommendations?limit=10",
            {
              method: "GET",
              headers: {
                Authorization: `Bearer ${token}`, // Envoi du badge d'accès
                "Content-Type": "application/json",
              },
            },
          );

          if (res.ok) {
            const data = await res.json();
            setRecoTF_IDF(data);
          }
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoadingTF_IDF(false);
      }
    }

    async function loadTopAlbum() {
      setLoadingTopAlbum(true);
      try {
        const res = await fetch("http://127.0.0.1:8000/topAlbum?limit=20", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (res.ok) {
          const data = await res.json();
          setTopAlbum(data);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoadingTopAlbum(false);
      }
    }

    async function loadUserPlaylists() {
      if (!isConnected || !userId) return;
      try {
        const token = localStorage.getItem("token");
        if (token) {
          const res = await fetch(
            `http://127.0.0.1:8000/users/${userId}/playlists`,
            {
              method: "GET",
              headers: { Authorization: `Bearer ${token}` },
            },
          );
          if (res.ok) {
            setUserPlaylists(await res.json());
          }
        }
      } catch (e) {
        console.error("Erreur lors de la récupération des playlists :", e);
      }
    }

    async function loadTopArtists() {
      setLoadingTopArtist(true);
      try {
        const res = await fetch("http://127.0.0.1:8000/topArtist?limit=20", {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        });

        if (res.ok) {
          const data = await res.json();
          setTopArtists(data); // On remplit le bon state
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoadingTopArtist(false);
      }
    }

    loadTracks();
    loadGRU();
    loadTF_IDF();
    loadTopAlbum();
    loadUserPlaylists();
    loadTopArtists();
    performSearch();
  }, [isConnected, userId, searchQuery]);

  const [modalOpen, setModalOpen] = useState(false);
  const [selectedTrackId, setSelectedTrackId] = useState<number | null>(null);

  const handleAddTrack = (trackId: number) => {
    setSelectedTrackId(trackId);
    setModalOpen(true);
  };

  return (
    <>
      <div className="accueil-layout">
        {isConnected && (
          <nav className="menu-favoris">
            <div>
              <ul className="list-aime">
                <li>Écouté récemment</li>
              </ul>

              <button
                className="btn-add-playlist"
                onClick={() => {
                  setSelectedTrackId(null);
                  setModalOpen(true);
                }}
              >
                Ajouter une Playlist
              </button>

              {isConnected && (
                <ul className="list-playlist">
                  {userPlaylists.map((pl) => (
                    <li
                      key={pl.playlist_id}
                      className="playlist-menu-item"
                      style={{ cursor: "pointer" }}
                      onClick={() => onOpenPlaylist(pl.playlist_id)}
                    >
                      {pl.playlist_name}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </nav>
        )}
        <main className="accueil-content">
          {searchQuery && (
            <>
              <h2>Résultats pour "{searchQuery}"</h2>
              {isSearching ? (
                <p>Recherche en cours...</p>
              ) : (
                <Carousel>
                  {searchResults.length > 0 ? (
                    searchResults.map((track) => (
                      <CarteChanson
                        key={`search-${track.track_id}`}
                        trackId={track.track_id}
                        title={track.track_title}
                        artist={track.artist_name}
                        pochette={track.album_image_file}
                        isConnected={isConnected}
                      />
                    ))
                  ) : (
                    <p>Aucun résultat trouvé.</p>
                  )}
                </Carousel>
              )}
            </>
          )}

          <h2>Musiques Populaires</h2>
          {error ? (
            <div
              style={{ color: "red", textAlign: "center", margin: "20px 0" }}
            >
              <p>⚠️ {error}</p>
            </div>
          ) : loadingTrack ? (
            <p>Chargement des musiques...</p>
          ) : (
            <Carousel>
              {tracks.map((track) => (
                <CarteChanson
                  key={track.track_id}
                  trackId={track.track_id}
                  title={track.track_title}
                  artist={track.artist_name}
                  // artist={track.artists.map(a => a.artist_name).join(", ")}
                  pochette={track.album_image_file}
                  isConnected={isConnected}
                  onAdd={() => handleAddTrack(track.track_id)}
                />
              ))}
            </Carousel>
          )}

          {isConnected && (
            <div className="reco-section">
              <h2>Selon vos recherches</h2>

              {loadingGRU ? (
                <div>
                  <p>Chargement des musiques...</p>
                </div>
              ) : recoTF_IDF.length > 0 ? (
                <Carousel>
                  {recoGRU.map((track) => (
                    <CarteChanson
                      key={track.track_id}
                      trackId={track.track_id}
                      title={track.track_title}
                      artist={track.artist_name}
                      // artist={track.artists.map(a => a.artist_name).join(", ")}
                      pochette={track.album_image_file}
                      isConnected={isConnected}
                      onAdd={() => handleAddTrack(track.track_id)}
                    />
                  ))}
                </Carousel>
              ) : (
                <div>
                  <p>
                    Vous n'avez pas encore d'historique, faites quelques
                    recherches !
                  </p>
                </div>
              )}

              <h2>Selon vos préférences</h2>

              {loadingTF_IDF ? (
                <div>
                  <p>Chargement des musiques...</p>
                </div>
              ) : recoTF_IDF.length > 0 ? (
                <Carousel>
                  {recoTF_IDF.map((track) => (
                    <CarteChanson
                      key={`reco-${track.track_id}`}
                      trackId={track.track_id}
                      title={track.track_title}
                      artist={track.artist_name}
                      pochette={track.album_image_file}
                      isConnected={isConnected}
                      onAdd={() => handleAddTrack(track.track_id)}
                    />
                  ))}
                </Carousel>
              ) : (
                <div>
                  <p>
                    Vous n'avez pas encore de préférences, écoutez quelques
                    musiques !
                  </p>
                </div>
              )}
            </div>
          )}

          <h2>Artistes Populaires</h2>
          {loadingTopArtist ? (
            <p>Chargement des artistes...</p>
          ) : topArtists.length > 0 ? (
            <Carousel>
              {topArtists.map((artist) => (
                <CarteArtist
                  key={artist.artist_id}
                  title={artist.artist_name}
                  creator={`${artist.artist_listens} écoutes`}
                  isConnected={isConnected}
                  onClick={() => {
                    console.log(
                      "1. Clic détecté dans Accueil pour l'id:",
                      artist.artist_id,
                    );
                    onOpenArtist(artist.artist_id);
                  }}
                />
              ))}
            </Carousel>
          ) : (
            <p>Aucun artiste trouvé.</p>
          )}

          <h2>Albums recommandés</h2>
          <Carousel>
            {topAlbum.map((album) => (
              <CarteAlbum
                key={album.album_id}
                title={album.album_title}
                artist={album.artist_name || "Artiste inconnu"}
                pochette={album.album_image_file}
                isConnected={isConnected}
                onClick={() => onOpenAlbum(album.album_id)}
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
  );
}
