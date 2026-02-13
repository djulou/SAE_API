import { useState } from 'react'
import Coeur from "./coeur"
import plus from "../assets/plus.svg"

type CarteChansonProps = {
  trackId: number
  title: string
  artist: string
  pochette: string
  isConnected: boolean
  onAdd?: () => void
}

function CarteChanson({
  trackId,
  title,
  artist,
  pochette,
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
        <img
          src={pochette}
          alt={`Pochette de ${title}`}
          className="pochette"
        />

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
              e.stopPropagation();
              onAdd();
            }}
            title="Ajouter à une playlist"
          >
            <img src={plus} alt="Ajouter" style={{ width: "30px", height: "30px" }} />
          </button>
        )}
      </article>
    </div>
  )
}

export default CarteChanson
