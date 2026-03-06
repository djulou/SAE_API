import { useState } from 'react'
import Coeur from "./coeur"

type CarteChansonProps = {
  trackId: number
  title: string
  artist: string
  pochette: string
  isConnected: boolean
  onAdd?: () => void
}
import GeneratedCover from "./GeneratedCover"

function CarteChanson({
  trackId,
  title,
  artist,
  isConnected,
  onAdd
}: CarteChansonProps) {
  const [isFavorite, setIsFavorite] = useState(false)

  const toggleFavorite = async () => {
    if (!isConnected) return

    const token = localStorage.getItem("token")
    if (!token) return

    try {
      if (!isFavorite) {
        const res = await fetch("http://127.0.0.1:8000/trackUserFavorite", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify({ track_id: trackId })
        })
        if (res.ok) setIsFavorite(true)
      } else {
        const res = await fetch(`http://127.0.0.1:8000/trackUserFavorite/${trackId}`, {
          method: "DELETE",
          headers: {
            "Authorization": `Bearer ${token}`
          }
        })
        if (res.ok) setIsFavorite(false)
      }
    } catch (e) {
      console.error("Erreur lors du toggle favori:", e)
    }
  }

  return (
    <div className="carte-chanson">
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
    </div>
  )
}

export default CarteChanson
