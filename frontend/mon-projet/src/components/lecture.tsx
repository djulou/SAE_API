import { useState, useRef, useEffect } from "react";
import Coeur from "./coeur";
import GeneratedCover from "./GeneratedCover";

type LectureProps = {
  trackId: number;
  title: string;
  artist: string;
  audioUrl: string; 
  isConnected: boolean;
  onAdd?: () => void;
};

function Lecture({
  trackId,
  title,
  artist,
  audioUrl,
  isConnected,
  onAdd,
}: LectureProps) {
  const [isPlaying, setIsPlaying] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  
  // Le like redevient local pour cette version
  const [isFavorite, setIsFavorite] = useState(false);

  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    if (audioRef.current) {
      isPlaying ? audioRef.current.play() : audioRef.current.pause();
    }
  }, [isPlaying, audioUrl]);

  const togglePlay = () => setIsPlaying(!isPlaying);

  const handleTimeUpdate = () => {
    if (audioRef.current) setCurrentTime(audioRef.current.currentTime);
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) setDuration(audioRef.current.duration);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = Number(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const formatTime = (time: number) => {
    const mins = Math.floor(time / 60);
    const secs = Math.floor(time % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const progressPercent = duration ? (currentTime / duration) * 100 : 0;

  return (
    <div className="lecture-page">
      <audio
        ref={audioRef}
        src={audioUrl}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        autoPlay
      />
      
      <section className="info-image">
        <div className="pochette-wrapper">
          <GeneratedCover title={title} />
        </div>
        <article className="description">
          <div className="text-info">
            <h3 style={{ color: "#ffffff", margin: 0 }}>{title}</h3>
            <p style={{ color: "var(--color-text-muted)", margin: 0 }}>{artist}</p>
          </div>
        </article>
      </section>

      <div className="ecoute-musique">
        <div className="player-controls" style={{ display: 'flex', justifyContent: 'center', marginBottom: '8px' }}>
          <button onClick={togglePlay} className="btn-main-play" style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
            <svg viewBox="0 0 24 24" fill="#ffffff" width="32" height="32">
              {isPlaying ? (
                <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
              ) : (
                <path d="M8 5v14l11-7z" />
              )}
            </svg>
          </button>
        </div>

        <div className="progress-container">
          <span className="time-label">{formatTime(currentTime)}</span>
          <div className="custom-progress-bar">
            <div className="progress-fill" style={{ width: `${progressPercent}%` }} />
            <input
              type="range"
              min="0"
              max={duration || 0}
              value={currentTime}
              onChange={handleSeek}
              className="progress-slider"
            />
          </div>
          <span className="time-label">{formatTime(duration)}</span>
        </div>
      </div>

      <div className="player-actions" style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        <Coeur
          isFavorite={isFavorite}
          isConnected={isConnected}
          toggleFavorite={(e) => {
            e.stopPropagation();
            setIsFavorite(!isFavorite); // Gestion locale simple
          }}
        />

        {isConnected && onAdd && (
          <button
            className="btn-plus"
            onClick={onAdd}
            style={{
              background: "transparent",
              border: "none",
              padding: "5px",
              display: "flex",
              alignItems: "center",
              cursor: "pointer"
            }}
          >
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#ffffff" strokeWidth="2.5">
              <path d="M12 5v14M5 12h14" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}

export default Lecture;