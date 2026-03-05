import { useState, useRef } from "react"
import Coeur from "./coeur"
import GeneratedCover from "./GeneratedCover"

type LectureProps = {
  trackId: number
  title: string
  artist: string
  audioUrl: string
  isConnected: boolean
  onAdd?: () => void
}

function Lecture({
  trackId,
  title,
  artist,
  audioUrl,
  isConnected,
  onAdd
}: LectureProps) {

  const [isFavorite, setIsFavorite] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)

  const audioRef = useRef<HTMLAudioElement | null>(null)

  const toggleFavorite = async () => {
    if (!isConnected) return

    const token = localStorage.getItem("token")
    if (!token) return

    try {

      const url = !isFavorite
        ? "http://127.0.0.1:8000/trackUserFavorite"
        : `http://127.0.0.1:8000/trackUserFavorite/${trackId}`

      const method = !isFavorite ? "POST" : "DELETE"

      const options: RequestInit = {
        method,
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        }
      }

      if (!isFavorite) {
        options.body = JSON.stringify({ track_id: trackId })
      }

      const res = await fetch(url, options)

      if (res.ok) {
        setIsFavorite(!isFavorite)
      }

    } catch (error) {
      console.error("Erreur lors du toggle favori :", error)
    }
  }

  const togglePlay = () => {
    if (!audioRef.current) return

    if (isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play()
    }

    setIsPlaying(!isPlaying)
  }

  const handleTimeUpdate = () => {
    if (!audioRef.current) return
    setCurrentTime(audioRef.current.currentTime)
  }

  const handleLoadedMetadata = () => {
    if (!audioRef.current) return
    setDuration(audioRef.current.duration)
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = Number(e.target.value)

    if (audioRef.current) {
      audioRef.current.currentTime = time
    }

    setCurrentTime(time)
  }

  const handleVolume = (e: React.ChangeEvent<HTMLInputElement>) => {
    const vol = Number(e.target.value)

    if (audioRef.current) {
      audioRef.current.volume = vol
    }

    setVolume(vol)
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, "0")}`
  }

  return (
    <div className="lecture-page">
        <section className="info-image">
        <div className="pochette-wrapper">
        <GeneratedCover title={title} />

        <div className="actions-overlay">
          <Coeur
            isFavorite={isFavorite}
            isConnected={isConnected}
            toggleFavorite={toggleFavorite}
          />
        </div>
        
      </div>
      <article className="description">
        <div>
          <h3>{title}</h3>
          <p>{artist}</p>
        </div>

        {isConnected && onAdd && (
          <button
            className="btn-plus"
            onClick={(e) => {
              e.stopPropagation()
              onAdd()
            }}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="30"
              height="30"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2.75"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M5 12h14" />
              <path d="M12 5v14" />
            </svg>
          </button>
        )}
      </article>
      </section>

      {/* <article className="description">
        <div>
          <h3>{title}</h3>
          <p>{artist}</p>
        </div>

        {isConnected && onAdd && (
          <button
            className="btn-plus"
            onClick={(e) => {
              e.stopPropagation()
              onAdd()
            }}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="30"
              height="30"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2.75"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M5 12h14" />
              <path d="M12 5v14" />
            </svg>
          </button>
        )}
      </article> */}

      <div className="ecoute-musique">

        <div className="audio-player">

          <audio
            ref={audioRef}
            src={audioUrl}
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
          />

          <button onClick={togglePlay} className="play-btn">
            {isPlaying ? "Pause" : "Play"}
          </button>

          <div className="progress-container">

            <span>{formatTime(currentTime)}</span>

            <input
              type="range"
              min={0}
              max={duration}
              value={currentTime}
              onChange={handleSeek}
            />

            <span>{formatTime(duration)}</span>

          </div>

        </div>

      </div>

      <div className="volume">

        <input
          type="range"
          min={0}
          max={1}
          step={0.01}
          value={volume}
          onChange={handleVolume}
        />

      </div>

    </div>
  )
}

export default Lecture
  