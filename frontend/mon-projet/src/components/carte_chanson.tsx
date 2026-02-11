import { useState } from 'react'
import Coeur from "./coeur"

type CarteChansonProps = {
  title: string
  artist: string
  pochette: string
  isConnected: boolean
  onAdd?: () => void
}

function CarteChanson({
  title,
  artist,
  pochette,
  isConnected,
  onAdd
}: CarteChansonProps) {
  const [isFavorite, setIsFavorite] = useState(false)

  const toggleFavorite = () => {
    if (!isConnected) return
    setIsFavorite(prev => !prev)
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
          {isConnected && onAdd && (
            <button
              className="btn-add-track"
              onClick={(e) => {
                e.stopPropagation();
                onAdd();
              }}
              title="Ajouter à une playlist"
            >
              +
            </button>
          )}
        </div>
      </div>

      <div className="description">
        <h3>{title}</h3>
        <p>{artist}</p>
      </div>
    </div>
  )
}

export default CarteChanson
