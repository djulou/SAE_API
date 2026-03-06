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
};

type AlbumData = {
  album_id: number;
  album_title: string;
  artist_name: string;
  album_image_file?: string;
  album_listens: number;
  track_count: number;
  album_date_released?: string;
};

type AlbumDetailProps = {
  albumId: number;
  isConnected: boolean;
};

// --- COMPOSANT LIGNE DE MUSIQUE ---
function AlbumTrackRow({
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
        {/* LOGIQUE : Bouton Play orange permanent. 
            Si actif et non survolé -> Animation. 
            Sinon (survolé ou inactif) -> Bouton Play orange */}
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
        <span className="track-name" style={{ color: isHovered || isActive ? "orange" : "var(--color-text)" }}>
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
export default function AlbumDetail({
  albumId,
  isConnected,
}: AlbumDetailProps) {
  const [album, setAlbum] = useState<AlbumData | null>(null);
  const [tracks, setTracks] = useState<TrackData[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTrack, setActiveTrack] = useState<TrackData | null>(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const resA = await fetch(`http://127.0.0.1:8000/album/${albumId}`);
        if (resA.ok) setAlbum(await resA.json());

        const resT = await fetch(`http://127.0.0.1:8000/album/${albumId}/tracks`);
        if (resT.ok) setTracks(await resT.json());
      } catch (err) {
        console.error("Erreur chargement album:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [albumId]);

  if (loading) return <div className="loading">Chargement de l'album...</div>;

  return (
    <div className="playlist-detail-container" style={{ paddingBottom: activeTrack ? "120px" : "40px" }}>
      <header className="playlist-header">
        <div className="playlist-cover-large">
          <GeneratedCover title={album?.album_title || "Album"} />
        </div>

        <div className="playlist-info">
          <span className="playlist-type">ALBUM</span>
          <h1 className="playlist-title-huge">{album?.album_title}</h1>
          <div className="playlist-meta-info">
            <span className="creator-bold">{album?.artist_name || "Artiste"}</span>
            <span className="bullet">•</span>
            <span>{album?.album_date_released ? new Date(album.album_date_released).getFullYear() : "N/A"}</span>
            <span className="bullet">•</span>
            <span>{tracks.length} titres</span>
            <span className="bullet">•</span>
            <span>{album?.album_listens} écoutes</span>
          </div>
        </div>
      </header>

      <div className="playlist-action-bar">
        <button className="btn-play-large" onClick={() => tracks.length > 0 && setActiveTrack(tracks[0])}>
          <svg viewBox="0 0 24 24" fill="black" width="28" height="28" style={{ marginLeft: "4px" }}>
            <path d="M8 5v14l11-7z" />
          </svg>
        </button>
      </div>

      <div className="tracklist-container">
        <div className="tracklist-header">
          {/* On remplace le "#" par une icône Play vide ou on laisse vide pour l'alignement */}
          <div className="col-index">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
               <path d="M8 5v14l11-7z" />
            </svg>
          </div>
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
            <AlbumTrackRow
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
            artist={album?.artist_name || "Artiste inconnu"}
            audioUrl={activeTrack.preview || ""}
            isConnected={isConnected}
            onAdd={() => console.log("Ajout playlist")}
          />
          <button className="btn-close-player" onClick={() => setActiveTrack(null)}>
            &times;
          </button>
        </div>
      )}
    </div>
  );
}