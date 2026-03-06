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
  album_title?: string;
  preview?: string;
};

type ArtistData = {
  artist_id: number;
  artist_name: string;
  artist_bio?: string;
  artist_location?: string;
  artist_image_file?: string;
  artist_favorites: number;
  artist_listens?: number;
};

type ArtistDetailProps = {
  artistId: number;
  isConnected: boolean;
};

// ============================================================================
// SOUS-COMPOSANT : Ligne de musique
// ============================================================================
function ArtistTrackRow({
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
        {/* LE BOUTON PLAY EST TOUJOURS VISIBLE (Sauf si la piste est active et non survolée) */}
        {isActive && !isHovered ? (
          <div className="playing-animation">
            <span className="bar"></span>
            <span className="bar"></span>
            <span className="bar"></span>
          </div>
        ) : (
          <svg 
            viewBox="0 0 24 24" 
            fill="orange" 
            width="20" 
            height="20" 
            style={{ 
                color: "orange", 
                filter: isHovered ? "brightness(1.2)" : "none",
                transition: "filter 0.2s"
            }}
          >
            <path d="M8 5v14l11-7z" />
          </svg>
        )}
      </div>

      <div className="col-title">
        <span 
          className="track-name" 
          style={{ color: isHovered || isActive ? "orange" : "var(--color-text)" }}
        >
          {track.track_title}
        </span>
        <span className="track-artist">{track.album_title || "Single"}</span>
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

// ============================================================================
// COMPOSANT PRINCIPAL
// ============================================================================
export default function ArtistDetail({ artistId, isConnected }: ArtistDetailProps) {
  const [artist, setArtist] = useState<ArtistData | null>(null);
  const [tracks, setTracks] = useState<TrackData[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTrack, setActiveTrack] = useState<TrackData | null>(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const resA = await fetch(`http://127.0.0.1:8000/artist/${artistId}`);
        if (resA.ok) setArtist(await resA.json());

        const resT = await fetch(`http://127.0.0.1:8000/artist/${artistId}/tracks`);
        if (resT.ok) setTracks(await resT.json());
      } catch (err) {
        console.error("Erreur chargement artiste:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [artistId]);

  if (loading) return <div className="loading">Chargement du profil artiste...</div>;

  return (
    <div className="playlist-detail-container" style={{ paddingBottom: activeTrack ? "120px" : "40px" }}>
      <header className="playlist-header artist-header">
        <div className="playlist-cover-large artist-image-circle">
          <GeneratedCover title={artist?.artist_name || "Artiste"} />
        </div>

        <div className="playlist-info">
          <span className="playlist-type">ARTISTE</span>
          <h1 className="playlist-title-huge">{artist?.artist_name}</h1>
          <div className="playlist-meta-info">
            <span>{artist?.artist_location || "Lieu inconnu"}</span>
            <span className="bullet">•</span>
            <span>{artist?.artist_listens?.toLocaleString() || 0} écoutes mensuelles</span>
          </div>
          {artist?.artist_bio && (
            <p className="artist-bio-preview">{artist.artist_bio.substring(0, 150)}...</p>
          )}
        </div>
      </header>
      
      <div className="tracklist-container">
        <h2 style={{ marginBottom: '20px', fontSize: '1.5rem', color: '#fff' }}>Populaires</h2>
        <div className="tracks-list">
          {tracks.slice(0, 10).map((track, idx) => (
            <ArtistTrackRow
              key={track.track_id}
              track={track}
              index={idx}
              isConnected={isConnected}
              isActive={activeTrack?.track_id === track.track_id}
              onPlay={() => setActiveTrack(track)}
            />
          ))}
        </div>
      </div>

      {activeTrack && (
        <div className="player-sticky-bar">
          <Lecture
            key={activeTrack.track_id}
            trackId={activeTrack.track_id}
            title={activeTrack.track_title}
            artist={artist?.artist_name || "Artiste"}
            audioUrl={activeTrack.preview || ""}
            isConnected={isConnected}
          />
          <button className="btn-close-player" onClick={() => setActiveTrack(null)}>
            &times;
          </button>
        </div>
      )}
    </div>
  );
}