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
  const [isFavorite, setIsFavorite] = useState(false);

  // --- Nouveaux états pour le Volume ---
  const [volume, setVolume] = useState(0.7); // Volume par défaut à 70%
  const [showVolumeBar, setShowVolumeBar] = useState(false);
  const [isMuted, setIsMuted] = useState(false);

  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    if (audioRef.current) {
      isPlaying ? audioRef.current.play() : audioRef.current.pause();
    }
  }, [isPlaying, audioUrl]);

  // Appliquer le volume à l'élément audio
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume;
    }
  }, [volume, isMuted]);

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

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    setVolume(val);
    if (val > 0) setIsMuted(false);
  };

  const toggleMute = () => setIsMuted(!isMuted);

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
            <p style={{ color: "var(--color-text-muted)", margin: 0 }}>
              {artist}
            </p>
          </div>
        </article>
      </section>

      <div className="ecoute-musique">
        <div
          className="player-controls"
          style={{
            display: "flex",
            justifyContent: "center",
          }}
        >
          <button
            onClick={togglePlay}
            className="btn-main-play"
            style={{ background: "none", border: "none", cursor: "pointer" }}
          >
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
            <div
              className="progress-fill"
              style={{ width: `${progressPercent}%` }}
            />
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

      <div
        className="player-actions"
        style={{ display: "flex", alignItems: "center", gap: "15px" }}
      >
        <div
          className="volume-control-container"
          onMouseEnter={() => setShowVolumeBar(true)}
          onMouseLeave={() => setShowVolumeBar(false)}
        >
          {/* La barre de volume qui flotte au-dessus */}
          {showVolumeBar && (
            <div className="volume-popover">
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={isMuted ? 0 : volume}
                onChange={handleVolumeChange}
                className="volume-slider-vertical"
              />
            </div>
          )}

          {/* L'icône cliquable */}
          <button onClick={toggleMute} className="btn-volume-icon">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="#ffffff">
              {isMuted || volume === 0 ? (
                <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z" />
              ) : (
                <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z" />
              )}
            </svg>
          </button>
        </div>

        <Coeur
          isFavorite={isFavorite}
          isConnected={isConnected}
          toggleFavorite={(e) => {
            e.stopPropagation();
            setIsFavorite(!isFavorite);
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
              cursor: "pointer",
            }}
          >
            <svg
              viewBox="0 0 24 24"
              width="24"
              height="24"
              fill="none"
              stroke="#ffffff"
              strokeWidth="2.5"
            >
              <path d="M12 5v14M5 12h14" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}

export default Lecture;
