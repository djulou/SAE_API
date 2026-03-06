import { useState, useEffect } from "react";
import Coeur from "./coeur";
import GeneratedCover from "./GeneratedCover";
import Lecture from "./lecture";

// --- TYPES ---
type TrackData = {
  track_id: number;
  track_title: string;
  track_duration: number;
  artist_name?: string;
  track_composer?: string;
  preview?: string; 
  playlistId?: number; 
  albumId?: number;
};

type PlaylistData = {
  playlist_id: number;
  playlist_name: string;
  playlist_listens: number;
  user_id: number;
  creator_pseudo?: string;
};

type PlaylistDetailProps = {
  playlistId: number;
  isConnected: boolean;
};

// --- COMPOSANT LIGNE DE MUSIQUE ---
function PlaylistTrackRow({
  track,
  isConnected,
  isActive,
  onPlay,
}: {
  track: TrackData;
  index: number;
  isConnected: boolean;
  isActive: boolean;
  onPlay: () => void;
}) {
  const [isHovered, setIsHovered] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div
      className={`track-row ${isActive ? "active-track" : ""}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onPlay}
      style={{ cursor: "pointer" }}
    >
      <div className="col-index">
        {isActive ? (
          <div className="playing-animation">
            <span className="bar" style={{ backgroundColor: "#ff9800" }}></span>
            <span className="bar" style={{ backgroundColor: "#ff9800" }}></span>
            <span className="bar" style={{ backgroundColor: "#ff9800" }}></span>
          </div>
        ) : (
          // Bouton Play toujours visible en orange
          <svg 
            viewBox="0 0 24 24" 
            fill="#ff9800" 
            width="18" 
            height="18"
          >
            <path d="M8 5v14l11-7z" />
          </svg>
        )}
      </div>

      <div className="col-title">
        <span 
          className="track-name" 
          style={{ color: isActive ? "#ff9800" : "var(--color-text)" }}
        >
          {track.track_title}
        </span>
        <span className="track-artist">
          {track.artist_name || track.track_composer || "Artiste inconnu"}
        </span>
      </div>

      <div className="col-actions">
        {(isHovered || isFavorite) && (
          <Coeur
            isFavorite={isFavorite}
            isConnected={isConnected}
            toggleFavorite={(e) => {
              e.stopPropagation();
              setIsFavorite(!isFavorite);
            }}
          />
        )}
      </div>

      <div className="col-duration">{formatDuration(track.track_duration)}</div>
    </div>
  );
}

// --- COMPOSANT PRINCIPAL ---
export default function PlaylistDetail({
  playlistId,
  isConnected,
}: PlaylistDetailProps) {
  const [playlist, setPlaylist] = useState<PlaylistData | null>(null);
  const [tracks, setTracks] = useState<TrackData[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTrack, setActiveTrack] = useState<TrackData | null>(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const token = localStorage.getItem("token");
        const headers: Record<string, string> = {};
        if (token) headers["Authorization"] = `Bearer ${token}`;

        const resP = await fetch(`http://127.0.0.1:8000/playlist/${playlistId}`, { headers });
        if (resP.ok) setPlaylist(await resP.json());

        const resT = await fetch(`http://127.0.0.1:8000/playlist/${playlistId}/tracks`, { headers });
        if (resT.ok) setTracks(await resT.json());
      } catch (err) {
        console.error("Erreur chargement playlist:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [playlistId]);

  if (loading) return <div className="loading">Chargement de la playlist...</div>;

  return (
    <div className="playlist-detail-container" style={{ paddingBottom: activeTrack ? "120px" : "40px" }}>
      <header className="playlist-header">
        <div className="playlist-cover-large">
          <GeneratedCover title={playlist?.playlist_name || "Playlist"} />
        </div>

        <div className="playlist-info">
          <span className="playlist-type">PLAYLIST</span>
          <h1 className="playlist-title-huge">{playlist?.playlist_name}</h1>
          <div className="playlist-meta-info">
            <span className="creator-bold">{playlist?.creator_pseudo || "Utilisateur"}</span>
            <span className="bullet">•</span>
            <span>{tracks.length} titres</span>
            <span className="bullet">•</span>
            <span>{playlist?.playlist_listens || 0} écoutes</span>
          </div>
        </div>
      </header>

      <div className="playlist-action-bar">
        {/* Gros bouton Play passé en Orange */}
        <button
          className="btn-play-large"
          style={{ backgroundColor: "#ff9800", border: "none" }}
          onClick={() => {
            if (tracks.length > 0) {
              setActiveTrack({ ...tracks[0], playlistId: playlist?.playlist_id });
            }
          }}
        >
          <svg viewBox="0 0 24 24" fill="black" width="28" height="28" style={{ marginLeft: "4px" }}>
            <path d="M8 5v14l11-7z" />
          </svg>
        </button>
      </div>

      <div className="tracklist-container">
        <div className="tracklist-header">
          <div className="col-index">#</div>
          <div className="col-title">Titre</div>
          <div className="col-actions"></div>
          <div className="col-duration">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
          </div>
        </div>

        <div className="tracks-list">
          {tracks.map((track, idx) => (
            <PlaylistTrackRow
              key={track.track_id}
              track={track}
              index={idx}
              isConnected={isConnected}
              isActive={activeTrack?.track_id === track.track_id}
              onPlay={() => setActiveTrack({ ...track, playlistId: playlist?.playlist_id })}
            />
          ))}
        </div>
      </div>

      {activeTrack && (
        <div className="player-sticky-bar">
          <Lecture
            key={activeTrack.track_id}
            trackId={activeTrack.track_id}
            playlistId={activeTrack.playlistId} 
            title={activeTrack.track_title}
            artist={activeTrack.artist_name || "Artiste inconnu"}
            audioUrl={activeTrack.preview || ""}
            isConnected={isConnected}
            onAdd={() => console.log("Ajout playlist")}
          />
          <button
            className="btn-close-player"
            onClick={() => setActiveTrack(null)}
          >
            &times;
          </button>
        </div>
      )}
    </div>
  );
}